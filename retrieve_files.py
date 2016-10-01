from ftplib import FTP
import config
import os


def main():
    if not os.path.exists(config.which_wiki):
        os.makedirs(config.which_wiki)
        print("making the directory")
    else:
        print("that directory exists")
    with FTP(host=config.ftp_site,
             user=config.ftp_user,
             passwd=config.ftp_pass,
             port=config.ftp_port,
             acct='') as ftp:
        ftp.cwd(config.which_wiki)
        all_files = ftp.nlst()
        for file in all_files:
            print ("retrieving {}".format(file))
            ftp.retrbinary('RETR {}'.format(file),
                           open(os.path.join(config.which_wiki, file), 'wb').write)


if __name__ == "__main__":
    main()