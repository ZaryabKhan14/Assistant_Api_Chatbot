class supertec_bot:
    def _init_(self):
        import openai



        def get_data():
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0',  # You can try different User-Agent strings if needed
            }

            payload = {'company_token': 'II@tNfQ70O'}

            response = requests.post("https://superteclabs.com/apis2/retrieveallusers.php", data=payload,
                                     headers=headers)

            data = response.json()
            return response.text

        self.get_data = get_data

        function_balance = {
            "type": "function",
            "function": {
                "name": "get_data",
                "description": "Retrieve the data from this ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "show me the all data "
                        },
                    },
                    "required": ["query"]
                }
            }
        }

        import os
        from dotenv import load_dotenv

        # Load environment variables from .env file
        load_dotenv()

        self.client = openai.OpenAI(api_key=os.environ['openai_api_key'])
        print(self.client)
        # Step 1: Create an Assistant
        # self.assistant = self.client.beta.assistants.create(
        #     name="library Support Chatbot",
        #     instructions="You are a personal Supertech support chatbot.",
        #     tools=[function_balance],
        #     model="gpt-3.5-turbo",
        # )




    def user_chat(self,query):
        import time
        # Step 2: Create a Thread
        thread = self.client.beta.threads.create()

        # Step 3: Add a Message to a Thread
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )

        # Step 4: Run the Assistant
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id="asst_tbdEcvmCNA4uFRPcxyVt8KNR",
            instructions=""
        )
        answer = None
        while True:
            # Retrieve the run status
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            # print(run_status.model_dump_json(indent=4))
            run_status.model_dump_json(indent=4)

            # If run is completed, get messages
            if run_status.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                # Loop through messages and print content based on role
                for msg in messages.data:
                    role = msg.role
                    content = msg.content[0].text.value
                    print(f"{role.capitalize()}: {content}")
                    answer = f"{role.capitalize()}: {content}"
                    break
                break
            elif run_status.status == 'requires_action':
                # print("Function Calling")
                required_actions = run_status.required_action.submit_tool_outputs.model_dump()
                # print('required action test: ',required_actions)
                tool_outputs = []
                import json
                for action in required_actions["tool_calls"]:
                    func_name = action['function']['name']
                    arguments = json.loads(action['function']['arguments'])

                    if func_name == "get_data":
                        output = self.get_data()
                        tool_outputs.append({
                            "tool_call_id": action['id'],
                            "output": output
                        })

                    else:
                        raise ValueError(f"Unknown function: {func_name}")

                print("Submitting outputs back to the Assistant...")
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            else:
                print("Waiting for the Assistant to process...")
                time.sleep(5)

        if answer is not None:
            print(f'this is my answer : ', answer)
            return answer