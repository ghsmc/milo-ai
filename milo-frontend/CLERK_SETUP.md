# Clerk Authentication Setup for Milo

This guide will help you set up Clerk authentication for the Milo application.

## 1. Create a Clerk Account

1. Go to [clerk.com](https://clerk.com) and sign up for a free account
2. Create a new application
3. Choose "React" as your framework
4. Select "Vite" as your build tool

## 2. Get Your API Keys

1. In your Clerk dashboard, go to "API Keys"
2. Copy your **Publishable Key** (starts with `pk_test_` or `pk_live_`)
3. Copy your **Secret Key** (starts with `sk_test_` or `sk_live_`)

## 3. Configure Environment Variables

Update your `.env.local` file with your Clerk keys:

```env
# Clerk Configuration
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here

# Clerk URLs
VITE_CLERK_SIGN_IN_URL=/sign-in
VITE_CLERK_SIGN_UP_URL=/sign-up
VITE_CLERK_AFTER_SIGN_IN_URL=/dashboard
VITE_CLERK_AFTER_SIGN_UP_URL=/onboarding

# Milo API
VITE_MILO_API_URL=http://localhost:8001
```

## 4. Configure Clerk Settings

In your Clerk dashboard:

### Authentication Methods
1. Go to "User & Authentication" → "Email, Phone, Username"
2. Enable the authentication methods you want:
   - Email address
   - Username (optional)
   - Phone number (optional)

### Social Providers (Optional)
1. Go to "User & Authentication" → "Social Connections"
2. Enable providers like Google, GitHub, etc.

### User Metadata
1. Go to "User & Authentication" → "User & Organization"
2. Enable "User metadata" to store onboarding data

## 5. Customize the UI (Optional)

The app is already configured with a dark theme that matches the Milo design. You can customize further in the Clerk dashboard:

1. Go to "Customize" → "Appearance"
2. Adjust colors, fonts, and styling to match your brand

## 6. Test the Integration

1. Start your development server: `npm run dev`
2. Navigate to `http://localhost:5173`
3. You should be redirected to the sign-in page
4. Create a new account or sign in
5. Complete the onboarding flow
6. Access the main dashboard

## 7. Production Deployment

When deploying to production:

1. **Upgrade to Clerk Pro Plan** (if not already done)
2. **Create Production Instance** in Clerk dashboard
3. **Update environment variables** with production Clerk keys:
   ```env
   VITE_CLERK_PUBLISHABLE_KEY=pk_live_YOUR_PRODUCTION_KEY_HERE
   ```
4. **Configure production domain** in Clerk dashboard under "Domains"
5. **Update redirect URLs** to your production domain
6. **Configure social providers** with production OAuth URLs
7. **Test production authentication** flow

### Production Checklist:
- [ ] Clerk Pro plan activated
- [ ] Production instance created
- [ ] Production publishable key updated
- [ ] Production domain configured in Clerk
- [ ] Social provider URLs updated
- [ ] Webhook URLs updated (if using)
- [ ] Authentication flow tested in production

## Features Included

✅ **Authentication Flow**
- Sign up with email
- Sign in with email
- Password reset
- Email verification

✅ **Onboarding Flow**
- Multi-step profile creation
- Data stored in Clerk user metadata
- Automatic redirect to dashboard

✅ **User Management**
- User profile button in header
- Sign out functionality
- Profile management

✅ **Dark Theme Integration**
- Matches Milo's dark theme
- Consistent styling throughout

## Troubleshooting

### Common Issues

1. **"Clerk publishable key not found"**
   - Make sure your `.env.local` file is in the root of the `milo-frontend` directory
   - Restart your development server after adding environment variables

2. **Redirect loops**
   - Check that your Clerk URLs are correctly configured
   - Ensure your routes match the configured URLs

3. **User metadata not saving**
   - Make sure "User metadata" is enabled in your Clerk dashboard
   - Check that the metadata keys match what's expected in the code

### Getting Help

- Check the [Clerk Documentation](https://clerk.com/docs)
- Review the [React Integration Guide](https://clerk.com/docs/quickstarts/react)
- Contact Clerk support if you encounter issues
