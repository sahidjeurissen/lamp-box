#!/usr/bin/python3
import os
import subprocess
import sys
import fileinput
import getpass
import readline

# define git urls, should become custom public repositories in gitlab
_GitUrls = {
    'yii2' : 'https://github.com/nenad-zivkovic/yii2-basic-template.git',
}

# replaces strings in a file
#
# @param replaceFile string // a file path
# @param replacements dict // dictionary (object in js) of replacements to be made in file
def searchReplaceInFile(replaceFile, replacements):
    lines = []
    with open(replaceFile) as infile:
        for line in infile:
            for src, target in replacements.items():
                line = line.replace(src, target)
            lines.append(line)
    with open(replaceFile, 'w') as outfile:
        for line in lines:
            outfile.write(line)

# prints Welcome instructions, gives the projectType options
#
# @param recheck bool False // param for recursive checking if no valid choice is given
def printWelcomeInstructions(recheck = False):
    if recheck:
        print('Invalid choice choose one of the following:')
    else:
        print('What kind of project do you want to create?')
    print('1) Yii2')
    print('2) Wordpress')
    choice = input().lower()

    print('You chose: ' + choice)

    validChoices = [
        'yii2',
        'wordpress'
    ]

    if not choice in validChoices:
        return printWelcomeInstructions(True)

    return choice

# asks a yes no question and returns a boolean based on the answer
#
# @param recheck bool False // param for recursive checking if no valid choice is given
# @return bool
def askBooleanQuestion(recheck = False):
    if recheck:
        print('Please answer with \'yes\' or \'no\'')

    answer = input().lower()
    if answer == 'yes':
        return True
    elif answer == 'no':
        return False
    else:
        return askBooleanQuestion(True)

# asks for a password with password repeat and reask on no match
#
# @param message string // message for password question
# @param messageRepeat string // message for password repeat question
# @param matchFailed bool False // param for recursive checking if passwords don't match
def getPasswordFromUser(message, messageRepeat, matchFailed = False):
    if matchFailed:
        print('Input doesn\'t match try again')
    pass1 = getpass.getpass(message)
    pass2 = getpass.getpass(messageRepeat)

    if not pass1 == pass2:
        return getPasswordFromUser(message, messageRepeat, True)
    return pass1

# main creation function for a Yii2 project
# is in charge of asking configuration questions and executing project creation
def createYii2Project():
    # ask project specific configuration
    print('Creating Yii2 project, please answer a couple of questions about your project:')
    appName = input('Application name:')
    appId = appName.lower().replace(' ', '_')
    themeName = input('Theme name:')

    # ask database specific configuration
    print('Thank you, and now a couple of questions about your database:')
    dbHost = input('Db host (leave blank for localhost):')
    if dbHost == '':
        dbHost = 'localhost'
    dbName = input('Db name:')
    dbUser = input('Db user:')
    dbPassword = getPasswordFromUser('Db password:', 'Repeat db password:')

    # clone project from git, wait for cloning to finish before going further with script execution
    cloneProcess = subprocess.Popen(['git', 'clone', '--depth=1', _GitUrls['yii2'], _ProjectDir])
    cloneProcess.wait()
    # remove .git folder since all we care about is the code not the versioning.
    subprocess.Popen(['sudo', 'rm', '-r', _ProjectDir + '/.git'])

    # search and replace the web.php config file
    searchReplaceInFile(_ProjectDir + '/_protected/config/web.php', {
        '\'id\' => \'basic\',' : '\'id\' => \'' + appId + '\',',
        '\'name\' => \'BASIC\'' : '\'name\' => \'' + appName + '\'',
        '@webroot/themes/light/views' : '@webroot/themes/' + themeName + '/views',
        '@web/themes/light' : '@webroot/themes/' + themeName
        })

    # TODO: find a way to clear everything from themes directory
    clearThemeProcess = subprocess.Popen(['rm', '-r', _ProjectDir + '/themes/light'])
    clearThemeProcess.wait()
    # make new theme directory
    subprocess.Popen(['mkdir', _ProjectDir + '/themes/' + themeName])

    # search and replace the db.php config file
    searchReplaceInFile(_ProjectDir + '/_protected/config/db.php', {
        '\'dsn\' => \'mysql:host=localhost;dbname=basic\',' : '\'dsn\' => \'mysql:host=' + dbHost + ';dbname=' + dbName + '\',',
        '\'username\' => \'root\'' : '\'username\' => \'' + dbUser + '\'',
        '\'password\' => \'root\'' : '\'password\' => \'' + dbPassword + '\''
        })

    # ask user if composer install should be executed
    print('Should we run the composer install for you?')
    # if composer install should be run do so
    if askBooleanQuestion():
        composerProcess = subprocess.Popen(['composer', 'install', '-d', _ProjectDir])
        composerProcess.wait()

    print('Do you want me to create a database for you?')
    if askBooleanQuestion():
        command = ['mysql', '-u', dbUser, '--password=' + dbPassword + '', '-h', dbHost, '-e', 'CREATE DATABASE ' + dbName + ';' ]
        print('executing command: ' + subprocess.list2cmdline(command))
        queryProcess = subprocess.Popen(command)
        queryProcess.wait()



def createWordpressProject():
    # ask database specific configuration
    print('To set up your wordpress installation we need some info on your database:')
    dbHost = input('Db host (leave blank for localhost):')
    if dbHost == '':
        dbHost = 'localhost'
    dbName = input('Db name:')
    dbUser = input('Db user:')
    dbPassword = getPasswordFromUser('Db password:', 'Repeat db password:')

    # Download wp core
    process = subprocess.Popen(['wp', 'core', 'download', '--locale=en_GB', '--path=' + _ProjectDir])
    process.wait()

    # Create wp config
    process = subprocess.Popen(['wp', 'core', 'config', '--dbhost=' + dbHost, '--dbname=' + dbName, '--dbuser=' + dbUser, '--dbpass=' + dbPassword, '--path=' + _ProjectDir])
    process.wait()

    # set permission for wp-config
    os.chmod(_ProjectDir + 'wp-config.php', 644)

    print('Wordpress is downloaded and set up.')
    print('Would you like me to run the install for you?')
    if askBooleanQuestion():
        command = ['mysql', '-u', dbUser, '--password=' + dbPassword + '', '-h', dbHost, '-e', 'CREATE DATABASE ' + dbName + ';' ]
        print('executing command: ' + subprocess.list2cmdline(command))
        queryProcess = subprocess.Popen(command)
        queryProcess.wait()

        # get wp install params
        print('To complete the installation we need a bit more information.')
        url = input('Local url:')
        title = input('Site title:')
        adminUser = input('Admin username:')
        adminPassword = getPasswordFromUser('Admin password:', 'Repeat password:')
        adminEmail = input('Admin email:')

        subprocess.Popen(['whoami'])

        # execute wp install
        process = subprocess.Popen(['sudo', 'wp', 'core', 'install', '--url=' + url, '--title=' + title, '--admin_name=' + adminUser, '--admin_password=' + adminPassword, '--admin_email=' + adminEmail, '--allow-root'])
        process.wait()



# get projectType from user
_ProjectType = printWelcomeInstructions()

# get current execution directory, execution directory can be different from script location
_CurrentDir = os.getcwd()

# check if second argument is given to script
if len(sys.argv) < 2:
    # if no second argument is given ask for the target directory for the project
    print('Where do you want your project to be placed, (leave blank for current directory).')
    _ProjectDir = input()
    if not _ProjectDir:
        _ProjectDir = _CurrentDir
else:
    # if second argument is given use second argument for target directory
    _ProjectDir = _CurrentDir + sys.argv[1]

if not _ProjectDir.endswith('/'):
    _ProjectDir = _ProjectDir + '/'

# call main project creation function
if _ProjectType == 'yii2':
    createYii2Project()
if _ProjectType == 'wordpress':
    createWordpressProject();


print('All done!')

# exit script and return to main command line
exit()
