// Base URL of the Shravan backend API.
//
// The old hardcoded LAN address (10.42.242.84) only worked on one network and
// silently broke every API call everywhere else. Point the app at the right
// server at build time instead:
//
//   flutter build apk --dart-define=API_BASE=https://your-backend.example.com/
//
// The value below is only a local-development fallback.
const String baseUrl = String.fromEnvironment(
  'API_BASE',
  defaultValue: 'http://127.0.0.1:8080',
);
