<script setup>

import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()


const email = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

async function login()
{
    if (!email.value.trim() || !password.value.trim()) {
        errorMessage.value = 'Email and password are required.'
        return
    }
    loading.value = true
    errorMessage.value = ''

    try{

        const response = await fetch('http://127.0.0.1:5000/api/login',
        {
            method: 'POST',

            headers: {
                'content-type': 'application/json'
            },

            credentials: 'include',

            body:JSON.stringify({
                'email': email.value,
                'password': password.value})
        })


        const data = await response.json()

        if (!response.ok) {
            errorMessage.value = data.message || 'Login failed'
            return
        }

        if (data.approval_status === 'pending') {
            errorMessage.value = 'Your account is pending approval. Please wait for admin approval.'
            return
        }

        if (data.user.role === 'admin') {
            await router.push('/admin/dashboard')
        }
        else if (data.user.role === 'staff') {
            await router.push('/staff/dashboard')
        }
        else {
            await router.push('/user/dashboard')
        }



    } catch (error) {

        console.error('Login error:', error)
        errorMessage.value = 'Unable to connect to the server'


        } finally {
            loading.value = false
        }
}

</script>

<template>

    <div class="grid-container-1">

        <form @submit.prevent="login" class="grid-container-2">

            <div class="loginform">

                <div class="title">
                    <p>Log in to Hi-Trek</p>
                </div>


        <div class="field">
            <input v-model="email" type="email" placeholder="email" required>
        </div>

        <div class="field">
            <input v-model="password" type="password" placeholder="password" required>
        </div>


        <div class="submit">
            <button type="submit">Log In</button>
        </div>

        <div class="register">
            <span>Don't have an account?</span>
            <RouterLink class="button" to="/register">
                Register Here
            </RouterLink>


        <p v-if="errorMessage" class="danger">
            {{ errorMessage }}
        </p>
        </div>
        </div>
    </form>

    <div></div>

</div>



</template>

<style scoped>


        .grid-container-1 {
            display:grid;
            grid-template-columns:1.25fr 1fr 1.25fr;
            align-items: center;
            height: 100vh;
        }

        .grid-container-2{


            border-radius: 1rem;
            border: 0.1rem solid #f2f2f2;
            padding: 2rem;
            grid-column: 2;


        }

        .loginform{

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


        .field input, .submit input {

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
            border-radius: 1rem;

        }

        input:focus {
            outline: none;
            border: 0.2rem solid #1877F2; /* Changes to a thicker blue border */
            border-radius: 0.3rem;
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

        .register{

            display: flex;
            flex-direction: column;
            align-items: center;
            font-size: 1rem;
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            margin-bottom: 0rem;
            padding-bottom: 0rem;

        }

        .register a{

            border:0.1rem solid #1877F2;
            border-radius: 1rem;
            font-size: 1rem;
            text-align: center;
        }

        a:hover{

            background-color: #e3e3e9;

        }

        .success{
            color: green;
            padding:0rem;
            font-size: 0.9rem;
        }

        .danger{
            color: red;
            font-size:0.9rem;
        }

</style>
