<script setup>

    import { ref } from 'vue'

    const username = ref('')
    const email = ref('')
    const password = ref('')
    const confirm_password = ref('')
    const role = ref('')

    const loading = ref(false)
    const message = ref('')
    const messageType = ref('')


    async function register() {

        message.value = ''
        messageType.value = ''

        if (!password.value.trim()) {
            message.value = 'Password is required.'
            messageType.value = 'error'
            return
        }
        if (password.value !== confirm_password.value) {
            message.value = 'Passwords do not match.'
            messageType.value = 'error'
            return
        }
        loading.value = true

        try {

            const response = await fetch(
                'http://127.0.0.1:5000/api/register',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify({
                    username:username.value,
                    email: email.value,
                    password: password.value,
                    role: role.value
                }
                )
            }
            )

            const data = await response.json()

            if(!response.ok){
                throw new Error(
                    data.message || 'Registeration failed'
                )
            }

            message.value = data.message || 'Registration successful!'
            messageType.value = 'success'

            username.value = ''
            email.value = ''
            password.value = ''
            confirm_password.value = ''
            role.value=''

        }

        catch (error) {
            message.value = error.message || 'Unable to connect to Flask.'
    }

        finally {
            loading.value = false
    }

    }
</script>


<template>
    <div class="grid-container-1">

        <div></div>
        <form class="grid-container-2" @submit.prevent="register">

        <div class="registerform">

            <div class="title">
                    <p>Get Started on Hi-Trek</p>
            </div>

             <div class="field">
                <input id="username" v-model="username" type="text" placeholder="username" required>
            </div>
            <!-- <label for="username">Username</label> -->
            <div class="field">
                <input id="email" v-model="email" type="email" placeholder="email" required>
            </div>

            <div class="field">
                <input id="password" v-model="password" type="password" placeholder="password" required>
            </div>

            <!-- <label for="password">Password</label> -->
            <div class="field">
                <input id="confirm_password" v-model="confirm_password" type="password" placeholder="retype_password" required>
            </div>

            <!-- <div class="role-row">
                <label for="role">I am a</label>

                <div class="role-field">
                    <select id="role" v-model="role" required>
                        <option value="user">User</option>
                        <option value="staff">Staff</option>
                    </select>
                </div>
            </div> -->

            <div class="submit">
                <button type="submit" :disabled="loading">
                {{ loading ? 'Registering...' : 'Register' }}
            </button>

            </div>

            <div class="login">
                    <p>Already have an account?</p>
                    <a class = "button" href="/login">Login Here</a>
            </div>

            <p v-if="message" :class="messageType" role="status"> {{ message }} </p>
        </div>
    </form>

    </div>




</template>

<style scoped>

        .html, .body{

            margin: 0%;
            height: 100%;

        }

        .grid-container-1{
            padding-top: 2rem;
            display:grid;
            grid-template-columns: 1.25fr 1fr 1.25fr;
            align-items: center;
        }

        .grid-container-2{


            border-radius: 1rem;
            border: 0.1rem solid #f2f2f2;
            padding: 2rem;
            grid-column: 2;


        }

        .registerform{

            display:flex;
            border-radius: 0.5rem;
            padding: 1rem;
            flex-direction: column;
            align-items: stretch;
            gap: 1rem;
            width: 100%;
            box-sizing: border-box;

        }

        .title{
            font-size: 1.5rem;
            font-weight: bold;
            border-bottom: 0.05rem solid black;
            padding-bottom: 0.2rem;

        }

        .title p {
            margin: 0;
    }

        .field{
            margin-top: 0.5rem;
            border: 0.15rem solid #f2f2f2;
            border-radius: 0.5rem;
            width: 100%;
            box-sizing: border-box;

        }

        .submit{
            margin-top: 0.5rem;
        }


        .field input, .submit input, .role-field select {

            font-size: 1rem;
            padding: 0.5rem;
            border-radius: 1rem;
            border: 0.2rem solid transparent;
            width: 100%;
            box-sizing: border-box;


        }

        .submit button {
            background-color: #1877F2;
            color: white;
            padding: 0.5rem;
            width: 100%;
            box-sizing: border-box;
            border: 0.2rem solid #1877F2;

        }

        input:focus{
            outline: none;
            border: 0.2rem solid #1877F2;
            border-radius: 0.2rem;
        }

        .role-field select {
            width: 100%;
            font-size: 1rem;
            padding: 0.5rem;
            border-radius: 1rem;
            box-sizing: border-box;
            outline: none;
        }

        .role-field select:focus {
            outline: none;
            border: 0.2rem solid #1877F2;
            border-radius: 1rem;
        }

        .role-row {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-top: 0.5rem;
        }

        .role-field {
            flex: 1;
            margin-top: 0;
        }

        .button{

            border-radius: 1rem;
            padding: 0.5rem;
            color: #1877F2;
            text-decoration: none;
            margin: 1rem;
            width: 100%;

        }

        .submit button:hover{


            background-color: white;
            color: #1877F2;
            cursor: pointer;
        }

        .login{

            display: flex;
            flex-direction: column;
            align-items: center;
            font-size: 1rem;
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            margin-bottom: 0rem;
            padding-bottom: 0rem;

        }

        .login a{

            border:0.1rem solid #1877F2;
            border-radius: 1rem;
            font-size: 1rem;
            text-align: center;
        }

        a:hover{

            background-color: #e3e3e9;

        }


    </style>

