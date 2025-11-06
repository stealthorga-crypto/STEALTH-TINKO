/**
 * Auth0 Post-Login Action
 * Marks phone/email as verified after successful Passwordless authentication
 * 
 * To use this action:
 * 1. Go to Auth0 Dashboard → Actions → Flows → Login
 * 2. Click "Build Custom" → Create new Action
 * 3. Name it: "Mark Passwordless Verified"
 * 4. Paste this code
 * 5. Deploy and add to your Login flow
 */

/**
 * Handler that will be called during the execution of a PostLogin flow.
 *
 * @param {Event} event - Details about the user and the context in which they are logging in.
 * @param {PostLoginAPI} api - Interface whose methods can be used to change the behavior of the login.
 */
exports.onExecutePostLogin = async (event, api) => {
  // Check if this is a passwordless login
  const connection = event.connection?.name || '';
  const strategy = event.connection?.strategy || '';
  
  console.log(`Login attempt via connection: ${connection}, strategy: ${strategy}`);
  
  // Handle Passwordless SMS
  if (strategy === 'sms' || connection === 'sms') {
    console.log('Passwordless SMS login detected');
    
    // Mark phone as verified in app_metadata
    api.user.setAppMetadata('phone_verified', true);
    api.user.setAppMetadata('phone_verified_at', new Date().toISOString());
    api.user.setAppMetadata('last_login_method', 'passwordless-sms');
    
    // Optionally add custom claims to the token
    api.idToken.setCustomClaim('https://tinko.app/phone_verified', true);
    api.accessToken.setCustomClaim('https://tinko.app/phone_verified', true);
    
    console.log(`Phone verified for user: ${event.user.user_id}`);
  }
  
  // Handle Passwordless Email
  if (strategy === 'email' || connection === 'email') {
    console.log('Passwordless Email login detected');
    
    // Mark email as verified in app_metadata
    api.user.setAppMetadata('email_verified', true);
    api.user.setAppMetadata('email_verified_at', new Date().toISOString());
    api.user.setAppMetadata('last_login_method', 'passwordless-email');
    
    // Optionally add custom claims to the token
    api.idToken.setCustomClaim('https://tinko.app/email_verified', true);
    api.accessToken.setCustomClaim('https://tinko.app/email_verified', true);
    
    console.log(`Email verified for user: ${event.user.user_id}`);
  }
  
  // Handle Google OAuth
  if (strategy === 'google-oauth2') {
    console.log('Google OAuth login detected');
    
    api.user.setAppMetadata('last_login_method', 'google-oauth2');
    api.user.setAppMetadata('social_provider', 'google');
    
    console.log(`Google login for user: ${event.user.user_id}`);
  }
  
  // Store last login timestamp
  api.user.setAppMetadata('last_login_at', new Date().toISOString());
  
  // Add user metadata to tokens (company, phone)
  const userMetadata = event.user.user_metadata || {};
  
  if (userMetadata.company) {
    api.idToken.setCustomClaim('https://tinko.app/company', userMetadata.company);
    api.accessToken.setCustomClaim('https://tinko.app/company', userMetadata.company);
  }
  
  if (userMetadata.phone) {
    api.idToken.setCustomClaim('https://tinko.app/phone', userMetadata.phone);
    api.accessToken.setCustomClaim('https://tinko.app/phone', userMetadata.phone);
  }
  
  console.log('Post-login action completed successfully');
};

/**
 * Handler that will be invoked when this action is resuming after an external redirect.
 *
 * @param {Event} event - Details about the user and the context in which they are logging in.
 * @param {PostLoginAPI} api - Interface whose methods can be used to change the behavior of the login.
 */
// exports.onContinuePostLogin = async (event, api) => {
// };
