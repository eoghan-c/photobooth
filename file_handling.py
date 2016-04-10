#!/usr/bin/env python
# Classes used to handle Photo Booth files

import os
import subprocess
import glob
import zipfile
import zlib

# Thanks http://stackoverflow.com/questions/26790916/python-3-backward-compatability-shlex-quote-vs-pipes-quote
try:
    from shlex import quote as cmd_quote
except ImportError:
    from pipes import quote as cmd_quote

# Set up the directories etc. to support photo storage and upload
local_file_dir        = os.path.join(os.sep, 'home', 'pi', 'photobooth', 'pics') # path to save PiCamera images to on Pi
local_upload_file_dir = os.path.join(os.sep, 'home', 'pi', 'photobooth', 'pics', 'upload') # path to save images to be uploaded

# Web server used for the photobooth
remote_account        = 'photobooth@somedomain.org.uk' # the username and host of the remote server
remote_file_dir       = 'public_html' # path to upload images to on web server
remote_url_prefix     = 'www.somedomain.org.uk' # the public website URL to the above remote_file_dir

class FileHandler(object):
    'Basic handling class for file operations'
    global local_file_dir
    global local_upload_file_dir
    global remote_account
    global remote_file_dir
    global remote_url_prefix

    def __init__(self):
        # Ensure photo storage and upload directories exist
        try:
            # We could use os.mkdir below - but unix 'mkdir -p' makes all directories 
            #    necessary in the entire path?
            # Ensure the 'upload' directory exists
            subprocess.check_call(["mkdir", "-p", local_upload_file_dir])

            # Ensure the 'pics' directory exists
            subprocess.check_call(["mkdir", "-p", local_file_dir])
        except subprocess.CalledProcessError as e:
            print "Error making local directories: ", e.returncode
            raise

    def get_local_file_dir(self):
        return local_file_dir

    def delete_files(self, the_dir):
        # Delete files in directory the_dir
        files = os.listdir(the_dir)
        for f in files:
            full_path = os.path.join(the_dir, f)

            # Only delete files, leave directories alone
            if os.path.isfile(full_path):
                self.delete_file(full_path)
    
    def delete_file(self, file_path):
        os.remove(file_path)

    def delete_local_files(self):
        self.delete_files(local_file_dir)

    def delete_upload_files(self):
        self.delete_files(local_upload_file_dir)

    def get_local_file_dir(self):
        return local_file_dir

    def get_upload_file_dir(self):
        return local_upload_file_dir

    def get_remote_file_dir(self):
        return remote_file_dir

    def get_remote_url_prefix(self):
        return remote_url_prefix

    def get_full_path(self, prefix, postfix):
        return os.path.join(prefix, postfix)

    def get_sorted_file_list(self, filepath_pattern):
        return sorted(glob.glob(filepath_pattern))

    # *** Zip the images up, ready for upload
    # *** Zip the images up, ready for upload    
    def zip_images(self, image_extension, zip_filename):
        print "Zipping files ..."
        file_pattern = os.path.join(local_upload_file_dir, "*photobooth*" + image_extension)
        files = sorted(glob.glob(file_pattern))

        with zipfile.ZipFile(os.path.join(local_upload_file_dir, zip_filename), 'w') as myzip:
            for curr_file in files:
                myzip.write(curr_file, arcname=os.path.basename(curr_file), compress_type=zipfile.ZIP_DEFLATED)

    # Copy file at src_filepath to dest_filepath
    def copy_file(self, src_filepath, dest_filepath):
        print "Copy file: " + src_filepath + " TO " + dest_filepath
        try:
            subprocess.check_call("cp " + src_filepath + " " + dest_filepath, shell=True)
        except subprocess.CalledProcessError as e:
            print "Error copying file: ", e.returncode
            raise

    # *** Upload files ***
    # file_defs is a list of lists containing:
    #     - full_local_filepath: the full path to file(s) to upload, including (e.g.) local_file_path
    #           full_local_filepath can include a file pattern to match a number of files
    #     - dest_filename: if "" use source filename, otherwise change destination filename (but retain extension)
    #     - full_remote_dir_path: the full path to the dir to upload files into, including remote_file_dir
    #     - num_files: if full_local_filepath includes a pattern that matches a number of files,
    #           this is the number of those files to upload. 0 means all files.
    #     - overwrite: if file exists in destination, overwrite if True, otherwise modify filename to make unique
    def upload_files(self, file_defs):
        print "Uploading files ... "

        for curr_file_def in file_defs:
            full_local_filepath, dest_filename, full_remote_dir_path, num_files, overwrite = curr_file_def

            # Find all the files that match our full_local_filepath (which may contain pattern)
            local_files = sorted(glob.glob(full_local_filepath))

            try:
                if len(local_files) > 0:
                    # Ensure the remote dir exits
                    # TODO: How expensive are calls to mkdir if dir already exists, 
                    #       better to check dir exists first?
                    subprocess.check_call("ssh " + remote_account + " 'mkdir -p " + 
                                          full_remote_dir_path + "'", shell=True)
                    curr_file_num = 1
                    for curr_file in local_files:
                        if (num_files is not 0) and (curr_file_num > num_files):
                            break

                        # Deal with the case where we want to alter the destination filename
                        curr_src_full_filename = os.path.basename(curr_file)
                        if dest_filename is "":
                            full_remote_filepath = cmd_quote(os.path.join(full_remote_dir_path, 
                                                       curr_src_full_filename))
                        else:
                            filename, extension = os.path.splitext(curr_src_full_filename)
                            full_remote_filepath = cmd_quote(os.path.join(full_remote_dir_path, 
                                                       dest_filename + extension))
                        
                        # Deal with the case where we do not want to overwrite the dest file
                        file_num = 2
                        if overwrite is False:
                            full_remote_filename = os.path.basename(full_remote_filepath)
                            while subprocess.call(['ssh', remote_account, 'test -e ' + 
                                                   full_remote_filepath]) == 0:
                                filename_no_ext, filename_ext = os.path.splitext(full_remote_filename)

                                full_remote_filepath = cmd_quote(os.path.join(full_remote_dir_path, 
                                            filename_no_ext + "_" + str(file_num) + filename_ext))
                                file_num += 1

                        subprocess.check_call("scp " + curr_file + " " + 
                                 remote_account + ":" + full_remote_filepath, shell=True)

                        curr_file_num += 1

            except subprocess.CalledProcessError as e:
                print "Error uploading files: ", e.returncode
                raise

        print "... upload finished."
