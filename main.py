# Dependencies
import requests
import os.path
import shutil
import time
import json

# By Kevin Helliwell

# This is ElvUI specific, but the underlying structure can be adapted to other addons.
# Adapting this to other addons is WIP.


class AddonManager:

    # Constructor logic
    def __init__(self, addon_dir, api_url, source_url):
        self.addon_dir = addon_dir
        self.api_url = api_url
        self.source_url = source_url

    # Methods

    # Checks if C:/Program Files (x86)/World of Warcraft/_retail_/Interface/Addons directory exists
    def check_addon_directory(self):
        if os.path.exists(self.addon_dir):
            return self
        else:
            exit(f"World of Warcraft addons directory doesn't exist.")

    # Gets version number from main ElvUI GitHub repo
    def get_version_number(self):
        api_data = requests.get(self.api_url).text
        parse_json_data = json.loads(api_data)
        version_number = parse_json_data.get("commit").get("commit").get("message")
        return version_number

    # Gets zip file name from main ElvUI GitHub repo by splitting and joining parts of the repo URL
    def get_zip_file_name(self):
        url_split_list = self.api_url.rsplit("/")
        zip_file_name = f"{url_split_list[-3]}-{url_split_list[-1]}"
        return zip_file_name

    # Checks if current version already exists in addons directory
    def check_local_version(self):
        # start_timer = time.time()
        addon_dir_list = os.listdir(self.addon_dir)
        zip_file_name = self.get_zip_file_name()
        version_number = self.get_version_number()
        if addon_dir_list.count(f"{zip_file_name} {version_number}.zip") > 0:
            # end_timer = time.time()
            # print(f"Done! Completed in {round((end_timer - start_timer), 2)} seconds\n")
            exit(f"Current version already exists in {self.addon_dir}\n")
        return self

    # Gets source zip file data from an API request before being written to a file in another function
    def get_source_zip_data(self):
        zip_file_data = requests.get(self.source_url).content
        return zip_file_data

    # Gets file path in addons directory for zip file data to be written to in another function
    def get_zip_file_path(self):
        zip_file_path = f"{self.addon_dir}/{self.get_zip_file_name()}"
        return zip_file_path

    # Writes zip file to addons directory
    # Appends version number for validation
    def manage_zip(self):
        zip_file_path = self.get_zip_file_path()
        version_number = self.get_version_number()
        file_name = f"{zip_file_path} {version_number}.zip"
        source_zip_data = self.get_source_zip_data()

        with open(file_name, "wb") as file:
            file.write(source_zip_data)

        # Specifies parameter for unzipping file
        archive_format = "zip"

        # Unzips file
        shutil.unpack_archive(file_name, self.addon_dir, archive_format)

        return self

    # Manages file paths in addons directory based on API data
    def manage_paths(self):
        # List of directory names to check for and move
        zip_file_path = self.get_zip_file_path()
        zip_dir_list = os.listdir(zip_file_path)

        # Generates directory paths and checks if they exist already
        for i in range(len(zip_dir_list)):

            # Checks if non-current version of ElvUI exists in addons directory
            # Implicitly checks if this program has been run before
            old_path = os.path.join(self.addon_dir, f"{zip_dir_list[i]}_OLD")
            old_path_exists = os.path.exists(old_path)

            # Checks if current version of ElvUI exists in addons directory
            # If current version not found, then there's no need to make room for it in the addons directory! :D
            current_path = os.path.join(self.addon_dir, zip_dir_list[i])
            current_path_exists = os.path.exists(current_path)

            # Checks if backup folders exist from previous updates
            if old_path_exists:
                shutil.rmtree(old_path)

            # Renames matching files if they exist already in addons directory
            if current_path_exists:
                os.rename(current_path, old_path)

            # Moves the files extracted from unzipped ElvUI folder to addons directory
            new_path = os.path.join(zip_file_path, zip_dir_list[i])
            shutil.move(new_path, self.addon_dir)

        # Removes empty unzipped ElvUI folder in addons directory
        shutil.rmtree(zip_file_path)

        return self


# Program
def main():
    # Greets user
    print("Welcome to your World of Warcraft (WoW) addon updater!")
    time.sleep(1)

    # Sets default path
    default_path = "C:/Program Files (x86)/World of Warcraft/_retail_/Interface/Addons"

    # Checks if default path needs to be changed for user
    path_check = str(input(f"Is {default_path} your World of Warcraft (WoW) addon directory? (y/n)\n"))
    if path_check == "n":
        new_path = str(input("Please enter the path of your World of Warcraft addon directory.\n"))
        addon_path = new_path
    else:
        addon_path = default_path

    # Lets user know something is happening
    print("Checking addon list for updates...")

    # Sets up addon list (WIP)
    elv_api_url = "https://api.github.com/repos/tukui-org/ElvUI/branches/main"
    elv_source_url = "https://github.com/tukui-org/ElvUI/archive/refs/heads/main.zip"
    elv_info = [elv_api_url, elv_source_url]
    addons_list = [elv_info]

    # Starts timer
    start_timer = time.time()

    # Loops through addons_list and updates each one
    for sub_list in addons_list:
        config_values = addon_path, sub_list[0], sub_list[1]
        addon_dir, api_url, source_url = config_values
        ui_manager = AddonManager(addon_dir, api_url, source_url)
        ui_manager.check_addon_directory().check_local_version().manage_zip().manage_paths()

    # End of Program
    end_timer = time.time()
    print(f"Done! Completed in {round((end_timer - start_timer), 2)} seconds.")


if __name__ == "__main__":

    # Runs program
    main()
