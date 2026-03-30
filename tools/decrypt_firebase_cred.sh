#!/bin/sh

# Decrypt the file
mkdir secrets
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --quiet --batch --yes --decrypt --passphrase="$FIREBASE_SECRET_PASSPHRASE" \
--output secrets/firebase_cred_secret.json resources/creds/firebase_cred.json.gpg