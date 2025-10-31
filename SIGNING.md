# Commit Signing

This repository uses GPG commit signing to ensure authenticity and integrity of commits.

## GPG Key Information

- **Key ID**: `0B5ED2912A37A5C0`
- **Key Type**: Ed25519
- **Owner**: Rob Sinclair <rob.sinclair@nhs.net>

## Verification

All commits to this repository are signed with the above GPG key. You can verify commit signatures using:

```bash
git log --show-signature
```

Or check a specific commit:

```bash
git verify-commit <commit-hash>
```

## Setting Up GPG Signing

To enable GPG signing for your commits:

1. Generate a GPG key:
   ```bash
   gpg --full-generate-key
   ```

2. List your keys and get the key ID:
   ```bash
   gpg --list-secret-keys --keyid-format LONG
   ```

3. Configure Git to use your key:
   ```bash
   git config --global user.signingkey YOUR_KEY_ID
   git config --global commit.gpgsign true
   ```

4. Export your public key and add it to GitHub:
   ```bash
   gpg --armor --export YOUR_KEY_ID
   ```

## GitHub Integration

The public key has been added to GitHub to display verified badges on signed commits.