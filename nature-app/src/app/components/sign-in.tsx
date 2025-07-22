"use client";
import { signIn } from "next-auth/react";

export function SignIn() {
  const credentialsAction = (formData: FormData) => {
    signIn("credentials", formData);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-white">
      <form
        action={credentialsAction}
        // Increased width here (e.g., from md:w-96 to md:w-1/3 or a specific pixel width like w-[400px])
        // Used a fixed width w-[400px] for a noticeable change. Adjust as needed.
        className="flex flex-col items-center p-8 border rounded-lg shadow-lg bg-white w-[400px] sm:w-[450px] md:w-[500px]"
        style={{ borderColor: "#136100" }} // Border color
      >
        <h1 className="mb-8 text-2xl font-bold" style={{ color: "#0E4700" }}>
          Login
        </h1>

        <label htmlFor="credentials-username" className="w-full mb-4">
          <span className="block mb-2" style={{ color: "#0E4700" }}>
            Username
          </span>
          <input
            type="username"
            id="credentials-username"
            name="username"
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2"
            style={{ backgroundColor: "rgba(19, 97, 0, 0.4)", borderColor: "#136100" }} // Input background and border
          />
        </label>

        <label htmlFor="credentials-password" className="w-full mb-6">
          <span className="block mb-2" style={{ color: "#0E4700" }}>
            Password
          </span>
          <input
            type="password"
            id="credentials-password"
            name="password"
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2"
            style={{ backgroundColor: "rgba(19, 97, 0, 0.4)", borderColor: "#136100" }} // Input background and border
          />
        </label>

        <input
          type="submit"
          value="Login"
          className="w-full px-4 py-2 text-white rounded-md cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2"
          style={{ backgroundColor: "#136100", borderColor: "#136100" }} // Button background and border (for focus ring)
        />
      </form>
    </div>
  );
}