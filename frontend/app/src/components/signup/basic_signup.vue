<template>
  <main class="bg-container">
    <div class="w-full max-w-sm bg-white p-8 rounded-lg shadow-lg">
      <h2 class="text-2xl sm:text-2xl font-semibold text-center text-gray-800 mb-4">
        Get started with <span class="logo">WotNot</span>
      </h2>
      <hr class="my-3 border-gray-300" />
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div class="w-full">
          <label for="username" class="block text-sm font-medium text-gray-700">Business Name</label>
          <input
            type="text"
            id="username"
            v-model="username"
            placeholder="Your Business Name"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            required
          />
        </div>
        <div class="w-full">
          <label for="email" class="block text-sm font-medium text-gray-700">Business Email Address</label>
          <input
            type="email"
            id="email"
            v-model="email"
            placeholder="your@email.com"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            required
          />
        </div>
        <div class="w-full">
          <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="Set a strong password"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            required
          />
          <div
            class="h-2 mt-2 rounded transition-all duration-300"
            :style="{ width: strengthWidth, backgroundColor: strengthColor }"
          ></div>
          <p class="text-sm mt-1 font-medium" :style="{ color: strengthColor }">
            {{ strengthLabel }}
          </p>
        </div>
        <div class="mt-4 text-sm text-center">
          <p class="mb-2 text-sm">
            By signing up you agree to the
            <router-link to="/terms" class="text-[#075e54] font-semibold">Terms</router-link>
            and
            <router-link to="/privacy" class="text-[#075e54] font-semibold">Privacy Policy</router-link>
          </p>
        </div>
        <div class="flex flex-col items-center">
          <button
            type="submit"
            class="w-full bg-gradient-to-r from-[#075e54] via-[#089678] to-[#075e54] text-white px-6 py-3 rounded-lg shadow-lg font-medium flex items-center justify-center hover:from-[#078478] hover:via-[#08b496] hover:to-[#078478] transition-all duration-300"
            :disabled="isLoading"
          >
            <span v-if="!isLoading">Get Account</span>
            <div v-else class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none"
                viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                </path>
              </svg>
              Creating Account...
            </div>
          </button>
        </div>
      </form>
      <p class="mt-4 text-center text-sm">
        Already have an account?
        <a
          href="#"
          class="text-[#075e54] font-semibold mb-4"
          @click.prevent="redirectLogin"
          >Login</a>
      </p>
    </div>
  </main>
</template>

<script>
import zxcvbn from "zxcvbn";
import { useToast } from "vue-toastification";

export default {
  name: "BasicSignUpForm",
  data() {
    return {
      apiUrl: process.env.VUE_APP_API_URL,
      username: "",
      email: "",
      password: "",
      isLoading: false,
    };
  },
  computed: {
    strengthScore() { return zxcvbn(this.password || "").score; },
    strengthLabel() { return ["Very Weak", "Weak", "Fair", "Good", "Strong"][this.strengthScore]; },
    strengthColor() { return ["#e53e3e", "#dd6b20", "#d69e2e", "#38a169", "#3182ce"][this.strengthScore]; },
    strengthWidth() { return `${(this.strengthScore / 4) * 100}%`; },
  },
  methods:.
  methods: {
    async handleSubmit() {
      const toast = useToast();
      this.isLoading = true;

      const formData = {
        username: this.username,
        email: this.email,
        password: this.password,
      };

      try {
        const response = await fetch(`${this.apiUrl}/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        });

        if (!response.ok) {
          let errorMessage = `Error: ${response.status}`;
          try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
          } catch (e) {
            console.error("Could not parse error response as JSON:", e);
          }
          throw new Error(errorMessage);
        }

        const data = await response.json();

        if (data.success) {
          toast.success("Account created successfully! Please log in.");
          this.$router.push("/");
        } else {
          throw new Error(data.message || "An unknown error occurred.");
        }
      } catch (error) {
        toast.error(error.message);
        console.error('Signup Error:', error);
      } finally {
        this.isLoading = false;
      }
    },
    redirectLogin() {
      this.$router.push("/");
    },
  },
};
</script>

<style scoped>
.logo { font-weight: 800; margin: 8px 0; padding-right: 30px; font-size: xx-large; color: #075e54; }
.bg-container { display: flex; align-items: center; justify-content: center; min-height: 100vh; background-image: url("@/assets/LoginPage.png"); background-position: center; padding: 0 16px; }
</style>

