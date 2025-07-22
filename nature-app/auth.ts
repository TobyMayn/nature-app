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
        const response = await fetch(`http://130.226.56.134/api/v1/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-urlencoded',
          },
          body: JSON.stringify(credentials),
        });
        const json = await response.json();
        console.log(json)

        if (!response.ok) throw new CredentialsSignin(json.detail);

        return json;
      }
    })
  ],
})