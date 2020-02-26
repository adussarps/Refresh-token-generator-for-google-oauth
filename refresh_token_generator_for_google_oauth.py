#!/usr/bin/python3.6
"""
Refresh token generator for google credentials
"""
import json
import optparse
import os
import subprocess
import sys

# The environment variable used to read credentials.
DSAPICRED_ENV = "DSAPICRED"


def RunCommand(cmd):
    print("running command: " + str(cmd))
    print("")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.communicate()
    return out[0]


def Login():
    """Collects tokens needed to access an api via OAuth2.

    Interactively collect a client id, a client secret, and a refresh token for
    accessing the requested scope. Users are asked to enter the client id
    and client secret and scope, and walked through the web authentication process to
    generate the refresh token.

    Raises:
      ValueError: response JSON could not be parsed, or has no refresh_token.
    """
    print("")
    print("This script requires setting up a Google API project.")
    print("If you have not done so, follow these instructions:")
    print("1. Visit https://console.developers.google.com")
    print('2. Create a new project and go to "API & auth -> credentials".')
    print("4. Create an OAuth2 client ID.")
    print(
        '5. When picking application type, choose "Installed application", '
        'type "Other".'
    )
    print("6. Enter the cliend id and client secret below:")
    print("")
    cid = input("Client ID: ").strip()
    csc = input("Client secret: ").strip()
    print("Please go to https://developers.google.com/oauthplayground/")
    print("and type the scope of your application (e.g analytics)")
    scope = input("Scope: ").strip()

    print("")
    print(
        "Please open the following URL in the browser to authenticate. "
        "When successful, the browser will display a code. "
        "Enter the code below."
    )
    print("")
    print(
        "https://accounts.google.com/o/oauth2/auth?"
        "scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2F"
        + scope
        + "&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
          "&response_type=code"
          "&access_type=offline"
          "&client_id=" + cid
    )
    print("")
    code = input("Code: ").strip()
    print("")
    output = RunCommand(
        [
            "curl",
            "-s",
            "--data",
            "code="
            + code
            + "&client_id="
            + cid
            + "&client_secret="
            + csc
            + "&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
            + "&grant_type=authorization_code",
            "https://accounts.google.com/o/oauth2/token",
        ]
    )
    json_output = json.loads(output)
    if "refresh_token" in json_output:
        print("Login successful.")
        print("")
        print('# DSAPI credentials: "client_id,client_secret,refresh_token"')
        print("{},\n{},\n{}".format(cid, csc, json_output["refresh_token"]))
        print("")
    else:
        raise ValueError("Missing refresh_token in response: %s" % output)


def GetDSApiCredOrDie(options):
    """Return API credentials passed into the script.

    Reads client id, client secret, and refresh token via the --cred flag or the
    DSAPICRED environment variable.

    Args:
      options: Flag values passed into the script.

    Returns:
      The credentials if found.

    Raises:
      Kills the program if no credentials are found.
    """
    # if options.cred is not None:
    #     cred = e.cred
    if DSAPICRED_ENV in os.environ:
        cred = os.environ[DSAPICRED_ENV].strip()
    else:
        print(
            """Cannot find credentials. You can pass them: client id, client secret, and refresh token via the --cred
            flag or the DSAPICRED environment variable.
        """)
        sys.exit(-1)
    return cred


def GetAccessTokenOrDie(options):
    """Generates a fresh access token using credentials passed into the script.

    Args:
      options: Flag values passed into the script.

    Returns:
      A fresh access token.

    Raises:
      ValueError: response JSON could not be parsed, or has no access_token.
    """
    cred = GetDSApiCredOrDie(options)
    [cid, csc, refresh_token] = cred.split(",")
    query_string_template = (
        "refresh_token=%s&client_id=%s&client_secret=%s"
        "&grant_type=refresh_token"
    )
    output = RunCommand(
        [
            "curl",
            "--data",
            query_string_template % (refresh_token, cid, csc),
            "https://accounts.google.com/o/oauth2/token",
        ]
    )
    json_output = json.loads(output)
    if "access_token" in json_output:
        return json_output["access_token"]
    else:
        raise ValueError("missing access_token in response: %s" % output)


def Logout(options):
    """Revoke the refresh token passed into the script.

    Args:
      options: Flag values passed into the script.
    """
    ds3_token = GetDSApiCredOrDie(options)
    [_, _, refresh_token] = ds3_token.split(",")
    RunCommand(
        [
            "curl",
            "https://accounts.google.com/o/oauth2/revoke?token="
            + refresh_token,
        ]
    )


def Main(argv):
    """The main program.

    Calls Login, Logout or RunREST depending on the command line arguments.

    Args:
      argv: Command line arguments.
    """
    parser = optparse.OptionParser()
    parser.add_option(
        "--login",
        dest="login",
        action="store_true",
        default=False,
        help="Generates a refresh token that does not expire over time.",
    )
    parser.add_option(
        "--logout",
        dest="logout",
        action="store_true",
        default=False,
        help="Invalidates a refresh token.",
    )

    (options, _) = parser.parse_args(argv)
    if options.login:
        Login()
    elif options.logout:
        Logout(options)
    else:
        parser.print_help()


if __name__ == "__main__":
    Main(sys.argv)
