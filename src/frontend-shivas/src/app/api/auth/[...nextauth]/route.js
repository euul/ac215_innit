import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"

const authOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const { username, password } = credentials

        // Replace with your own authentication logic (e.g., check the database)
        const user = await authenticateUser(username, password)

        if (user) {
          return user // Return the user object if authentication is successful
        } else {
          return null // Return null if authentication fails
        }
      },
    }),
  ],
  session: {
    strategy: "jwt",
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.username = user.username
      }
      return token
    },
    async session({ session, token }) {
      session.user.id = token.id
      session.user.username = token.username
      return session
    },
  },
}

export const handler = NextAuth(authOptions)

export async function POST(req) {
  return handler(req)
}
