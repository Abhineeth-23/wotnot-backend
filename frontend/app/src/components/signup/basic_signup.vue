<template>
  <div class="bg-container">
    <div class="max-w-md w-full bg-white p-8 rounded-lg shadow-lg">
      <h2
        class="text-2xl sm:text-2xl font-semibold text-center text-gray-800 mb-4"
      >
        Get started with <span class="logo">WotNot</span>
      </h2>

      <hr class="my-3 border-gray-300" />

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div class="w-full">
          <label for="username" class="block text-sm font-medium text-gray-700"
            >Business Name</label
          >
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
          <label for="email" class="block text-sm font-medium text-gray-700"
            >Business Email Address</label
          >
          <input
            type="email"
            id="email"
            v-model="email"
            placeholder="Your Business Email"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            required
          />
        </div>

        <div class="w-full">
          <label for="password" class="block text-sm font-medium text-gray-700"
            >Password</label
          >
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="Set Password"
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
            <router-link
              to="/terms-and-privacy#terms-and-conditions"
              class="text-[#075e54] font-semibold"
              >Terms</router-link
            >
            and
            <router-link
              to="/terms-and-privacy#privacy-policy"
              class="text-[#075e54] font-semibold"
              >Privacy Policy</router-link
            >
          </p>
        </div>

        <div class="flex flex-col items-center pt-4">
          <button
            type="submit"
            class="w-full bg-gradient-to-r from-[#075e54] via-[#089678] to-[#075e54] text-white px-6 py-3 rounded-lg shadow-lg font-medium flex items-center justify-center hover:from-[#078478] hover:via-[#08b496] hover:to-[#078478] transition-all duration-300"
          >
            Get Account
          </button>

          <p class="mt-4 text-center text-sm">
            Already have an account?
            <a
              href="#"
              class="text-[#075e54] font-semibold mb-4"
              @click.prevent="redirectLogin"
              >Login</a
            >
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import zxcvbn from "zxcvbn";
import { useToast } from "vue-toastification";

export default {
  data() {
    return {
      apiUrl: process.env.VUE_APP_API_URL,
      username: "",
      email: "",
      password: "",
    };
  },
  name: "BasicSignUpForm",
  computed: {
    strengthScore() {
      return zxcvbn(this.password || "").score;
    },
    strengthLabel() {
      return ["Very Weak", "Weak", "Fair", "Good", "Strong"][
        this.strengthScore
      ];
    },
    strengthColor() {
      return ["#e53e3e", "#dd6b20", "#d69e2e", "#38a169", "#3182ce"][
        this.strengthScore
      ];
    },
    strengthWidth() {
      return `${(this.strengthScore / 4) * 100}%`;
    },
  },
  methods: {
    handleSubmit() {
      const toast = useToast();
      const formData = {
        username: this.username,
        email: this.email,
        password: this.password,
      };

      if (!formData.username || !formData.email || !formData.password) {
        toast.error("Please fill in all required fields.");
        return;
      }

      // We'll assume your backend endpoint is /api/register
      fetch(`${this.apiUrl}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })
        .then((response) => {
            if (!response.ok) {
                // If response is not ok, parse the error json
                return response.json().then(errorData => {
                    throw new Error(errorData.detail || 'Failed to create account.');
                });
            }
            return response.json();
        })
        .then((data) => {
          toast.success("Account created successfully!");
          // Reset form
          this.username = "";
          this.email = "";
          this.password = "";
          this.$router.push("/"); // Redirect to login
        })
        .catch((error) => {
            console.error(error);
            toast.error(error.message || "An error occurred. Please try again.");
        });
    },
    redirectLogin() {
      this.$router.push("/");
    },
  },
};
</script>

<style scoped>
/* Styles are unchanged */
.logo {
  font-weight: 800;
  margin: 8px 0;
  padding-right: 30px;
  font-size: 30px;
  color: #075e54;
}
.bg-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-image: url("@/assets/LoginPage.png");
  background-position: center;
  padding: 0 16px;
}
</style>
