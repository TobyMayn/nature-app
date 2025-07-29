import { CredentialsSignin } from '@auth/core/errors';
import NextAuth from "next-auth";
import CredentialsProvider from 'next-auth/providers/credentials';
 
export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    CredentialsProvider({
      credentials: {
        username: { label: "Username", type: "username" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const formData = new URLSearchParams();
        formData.append('grant_type', 'password');
        formData.append('username', credentials.username as string);
        formData.append('password', credentials.password as string);
        
        console.log('Sending request with body:', formData.toString());
        try {
          const response = await fetch(`http://130.226.56.134/api/v1/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData.toString(),
          });

          const json = await response.json();
          console.log('Auth response:', json);

          if (!response.ok) {
            console.error('Auth failed:', json);
            throw new CredentialsSignin(json.detail || 'Authentication failed');
          }

          // Return user object with token stored in a way that persists in session
          return {
            id: credentials.username as string, // Use username as unique identifier
            name: credentials.username as string,
            email: credentials.username as string,
            accessToken: json.access_token,
            tokenType: json.token_type,
          };
        } catch (e: unknown) {
          console.error('Auth error:', (e as Error).message); 
          throw new CredentialsSignin('Network error or invalid credentials');
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      // Persist the OAuth access_token to the token right after signin
      if (user) {
        token.accessToken = user.accessToken;
        token.tokenType = user.tokenType;
      }
      return token;
    },
    async session({ session, token }) {
      // Send properties to the client
      session.accessToken = token.accessToken;
      session.tokenType = token.tokenType;
      return session;
    },
  },
})