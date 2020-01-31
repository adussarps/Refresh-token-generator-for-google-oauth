# Refresh-token-generator-for-google-oauth
A little script to help generate refresh tokens for authenticating to a google api via oAuth.

This script was taken from a google repository and adapted to be a litte more
generic.

## Requirements

You need to have **python3** installed.

## Usage

Run  `python refresh_token_generator_for_google_oauth.py`

You can provide two options ``-login`` to generate an access token, and 
``-logout`` to revoke one.