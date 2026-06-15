# Shipping Scorched Mobile to TestFlight

This project wraps the HTML5 game in a native iOS shell using
[Capacitor](https://capacitorjs.com/), and ships it to TestFlight via a GitHub
Actions + fastlane pipeline running on a macOS runner.

You do **not** need a Mac — CI builds and uploads for you. If you do have a Mac,
you can also build locally (see the last section).

---

## 0. The bundle ID is a placeholder

The app's bundle identifier is set to `com.fmdc.scorched` **as a placeholder**.
You must change it to a bundle ID you own. If you change it, update it in **all
three** places so everything stays consistent:

1. `capacitor.config.ts` → `appId`
2. The `APP_IDENTIFIER` GitHub repo secret
3. `fastlane/Appfile` → `app_identifier` (it reads `APP_IDENTIFIER`, so just
   setting the secret is enough; the literal fallback is only used locally)

---

## 1. Prerequisites

- An **Apple Developer Program** membership ($99/year) — required to upload to
  TestFlight.
- Admin/access to this GitHub repository so you can add **repository secrets**.
- A Mac is **NOT required** (CI uses a `macos-14` runner). It's optional for
  local builds.

---

## 2. Register the App ID and create the app record

### a) Create the App ID (bundle identifier)

1. Go to <https://developer.apple.com/account/resources/identifiers/list>.
2. Click **+**, choose **App IDs** → **App**.
3. Set the **Bundle ID** to the one you own (e.g. `com.yourcompany.scorched`).
4. Save. This is the value you'll use everywhere `com.fmdc.scorched` appears.

### b) Create the app in App Store Connect

1. Go to <https://appstoreconnect.apple.com/apps>.
2. Click **+** → **New App**.
3. Platform **iOS**, pick the **Bundle ID** you just registered, set a name and
   SKU. Save.

This creates the app record TestFlight builds attach to.

---

## 3. Create an App Store Connect API key (.p8)

Used for password-free, 2FA-free uploads.

1. Go to <https://appstoreconnect.apple.com/access/integrations/api>
   (Users and Access → Integrations → App Store Connect API).
2. Click **+** to generate a key. Give it the **App Manager** role.
3. **Download the `.p8` file** — you can only download it once.
4. Note the **Key ID** (next to the key) and the **Issuer ID** (shown at the top
   of the page).

You now have three things: the `.p8` file, the **Key ID**, and the **Issuer ID**.

Base64-encode the key so it can be stored as a secret:

```sh
base64 -i AuthKey_XXXXXXXXXX.p8 | pbcopy   # copies to clipboard (macOS)
# Linux: base64 -w0 AuthKey_XXXXXXXXXX.p8
```

---

## 4. Export a distribution certificate (.p12)

You need an **Apple Distribution** certificate exported as a `.p12`.

If you have a Mac with the certificate in Keychain Access:

1. Open **Keychain Access** → **My Certificates**.
2. Find your **Apple Distribution** certificate (it has a private key under it).
3. Right-click → **Export…** → save as `.p12` and set a password (remember it —
   that's `DIST_CERT_PASSWORD`).

If you don't have one yet, create it at
<https://developer.apple.com/account/resources/certificates/list> (type:
**Apple Distribution**), then import it into Keychain and export as above.

Base64-encode it:

```sh
base64 -i dist_cert.p12 | pbcopy
# Linux: base64 -w0 dist_cert.p12
```

---

## 5. Create an App Store provisioning profile (.mobileprovision)

1. Go to <https://developer.apple.com/account/resources/profiles/list>.
2. Click **+** → **App Store** (under Distribution).
3. Select your **App ID** (the bundle ID from step 2a).
4. Select the **distribution certificate** from step 4.
5. Name it (e.g. "Scorched App Store"), **download** the `.mobileprovision`.

Base64-encode it:

```sh
base64 -i profile.mobileprovision | pbcopy
# Linux: base64 -w0 profile.mobileprovision
```

---

## 6. Find your Team ID

Your **Team ID** is the 10-character string shown at
<https://developer.apple.com/account> under **Membership details**
(e.g. `ABCDE12345`).

---

## 7. Add the GitHub repository secrets

In your repo: **Settings → Secrets and variables → Actions → New repository
secret**. Add each of these:

| Secret                | What it is                                                                 |
| --------------------- | -------------------------------------------------------------------------- |
| `ASC_KEY_ID`          | App Store Connect API **Key ID** (from step 3)                             |
| `ASC_ISSUER_ID`       | App Store Connect **Issuer ID** (from step 3)                              |
| `ASC_API_KEY_BASE64`  | base64 of the `.p8` API key file (from step 3)                             |
| `APPLE_TEAM_ID`       | Your 10-char Apple Developer **Team ID** (from step 6)                     |
| `APP_IDENTIFIER`      | Your app **bundle ID** (e.g. `com.yourcompany.scorched`)                   |
| `DIST_CERT_BASE64`    | base64 of the distribution certificate `.p12` (from step 4)               |
| `DIST_CERT_PASSWORD`  | the password you set when exporting the `.p12` (from step 4)              |
| `PROV_PROFILE_BASE64` | base64 of the App Store `.mobileprovision` (from step 5)                   |

That's the complete list — eight secrets.

---

## 8. Trigger the build

Either:

- **Push a version tag:**

  ```sh
  git tag v1.0.0
  git push origin v1.0.0
  ```

- **Or run it manually:** repo **Actions** tab → **iOS TestFlight** → **Run
  workflow**.

The workflow will: install deps, run `npm run build` (copies the game into
`www/`), generate the native iOS project with `npx cap add ios`, sync, and run
`fastlane beta` to build and upload. Because
`skip_waiting_for_build_processing: true` is set, the job finishes as soon as
the upload completes; the build then takes a few minutes to process in
App Store Connect before it appears in TestFlight.

> First upload note: a brand-new app may require you to accept export-compliance
> and provide test info in App Store Connect before testers can install.

---

## 9. (Optional) Build locally on a Mac

You don't need this for CI, but it's handy for debugging.

```sh
npm install
npm run build        # copies index.html, sw.js, manifest.webmanifest, icon.svg -> www/
npx cap add ios      # generates the native ios/ project (first time only)
npx cap sync ios     # copies web assets + plugins into the native project
npx cap open ios     # opens the project in Xcode
```

In Xcode:

1. Select the **App** target → **Signing & Capabilities**.
2. Set your **Team** (and bundle identifier if you changed it).
3. **Product → Archive**.
4. In the Organizer: **Distribute App → TestFlight (App Store Connect)**.

---

## File reference

- `package.json` — npm scripts (`build`, `cap:sync`, `cap:add-ios`) + Capacitor deps.
- `capacitor.config.ts` — app id/name, `webDir: www`, iOS background + content inset.
- `scripts/build-web.js` — copies the four web files into `www/`.
- `fastlane/Fastfile` — the `beta` lane (signing, build, TestFlight upload).
- `fastlane/Appfile` — identifiers read from env.
- `.github/workflows/ios-testflight.yml` — the CI pipeline.
