const {
    browserSupportsWebAuthn,
    startRegistration,
    startAuthentication,
    browserSupportsWebAuthnAutofill,
} = SimpleWebAuthnBrowser;

console.log(browserSupportsWebAuthn())