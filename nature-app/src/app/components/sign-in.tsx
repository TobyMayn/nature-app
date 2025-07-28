"use client";
import { signIn } from "next-auth/react";
import { useState } from "react";

export function SignIn() {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const credentialsAction = async (formData: FormData) => {
    const username = formData.get("username") as string;
    const password = formData.get("password") as string;
    
    setError(null);
    setIsLoading(true);
    
    console.log("Form data:", { username, password }); // Debug log
    
    const result = await signIn("credentials", {
      username: username,
      password: password,
      redirect: false, // Don't redirect automatically
    });

    setIsLoading(false);

    if (result?.error) {
      setError("Invalid username or password. Please try again.");
    } else {
      // Successful login - redirect to desired page
      window.location.href = "/";
    }
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

        {error && (
          <div className="w-full mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md">
            {error}
          </div>
        )}

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
          value={isLoading ? "Signing in..." : "Login"}
          disabled={isLoading}
          className="w-full px-4 py-2 text-white rounded-md cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ backgroundColor: "#136100", borderColor: "#136100" }} // Button background and border (for focus ring)
        />
      </form>
    </div>
  );
}