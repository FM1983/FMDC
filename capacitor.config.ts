import type { CapacitorConfig } from '@capacitor/cli';

// IMPORTANT: `appId` MUST match the bundle ID you register in your Apple
// Developer account and App Store Connect. `com.fmdc.scorched` is a PLACEHOLDER
// — change it to a bundle ID you own. If you change it here, also update:
//   - the `APP_IDENTIFIER` GitHub Actions secret
//   - fastlane/Appfile (app_identifier)
const config: CapacitorConfig = {
  appId: 'com.fmdc.scorched',
  appName: 'Scorched Mobile',
  // Static web app: `npm run build` copies the game files into `www/`.
  webDir: 'www',
  ios: {
    // Lets the web content extend under the status bar / safe areas and lets
    // the CSS handle insets (the game canvas wants the full screen).
    contentInset: 'always',
    // Match the game's dark background so there is no white flash on launch.
    backgroundColor: '#0b1020',
  },
};

export default config;
