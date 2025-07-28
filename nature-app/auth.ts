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

          // NextAuth expects a user object with at least an id
          return {
            id: json.access_token, // or use another unique identifier from your API
            ...json
          };
        } catch (e: unknown) {
          console.error('Auth error:', (e as Error).message); 
          throw new CredentialsSignin('Network error or invalid credentials');
        }
      }
    })
  ],
})