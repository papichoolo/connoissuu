from julep import Client
import os
from dotenv import load_dotenv
import time
import yaml

load_dotenv(override=True)
JULEP_API_KEY = os.environ["JULEP_API_KEY"]

# Create a Julep client
client = Client(api_key=JULEP_API_KEY, environment="production")

agent = client.agents.create(
    name="Foodie Tour Guide",
    model="claude-3.5-sonnet",
    about="An expert food tour guide that creates weather-aware culinary experiences."
)

task_def = yaml.safe_load("""
# yaml-language-server: $schema=https://raw.githubusercontent.com/julep-ai/julep/refs/heads/dev/schemas/create_task_request.json
name: Weather-Aware Foodie Tour Planner
description: Creates a delightful one-day foodie tour with weather-appropriate dining recommendations and iconic local dishes.

########################################################
####################### INPUT SCHEMA ##################
########################################################                       
input_schema:
  type: object
  properties:
    locations:
      type: array
      items:
        type: string
      description: The cities to create foodie tours for.

########################################################
####################### TOOLS ##########################
########################################################

tools:
- name: weather
  type: integration
  integration:
    provider: weather
    setup:
      openweathermap_api_key: d6670dd2de9213be040b32b7ae27749e

- name: internet_search
  type: integration
  integration:
    provider: brave
    setup:
      brave_api_key: BSA5v5UrtToBZiAcLpaDROooJbeADsL

########################################################
####################### MAIN WORKFLOW ##################
########################################################

main:
# Step 0: Fetch weather data for each location
- over: $ steps[0].input.locations
  map:
    tool: weather
    arguments:
      location: $ _

# Step 1: Search for iconic local dishes for each location
- over: $ steps[0].input.locations
  map:
    tool: internet_search
    arguments:
      query: $ 'iconic local dishes must try ' + _ 

# Step 2: Search for top-rated restaurants for each location
- over: $ steps[0].input.locations
  map:
    tool: internet_search
    arguments:
      query: $ 'best restaurants top rated dining with local cuisines' + _ 

# Step 3: Zip locations, weather, dishes, and restaurants into tuples
- evaluate:
    zipped: |-
      $ list(
        zip(
          steps[0].input.locations,
          [output.get('result', 'Weather data unavailable') for output in steps[0].output],
          [output.get('result', 'Dish data unavailable') for output in steps[1].output],
          [output.get('result', 'Restaurant data unavailable') for output in steps[2].output]
        )
      )

# Step 4: Create a foodie tour itinerary for each location
- over: $ _['zipped']
  parallelism: 3
  map:
    prompt:
    - role: system
      content: >-
        You are an expert food tour guide and culinary consultant.
        Your task is to create a delightful one-day foodie tour that considers weather conditions
        for indoor/outdoor dining recommendations.

        For each location, you should:
        1. Analyze the weather to suggest indoor or outdoor dining preferences
        2. Identify 3 iconic local dishes from the provided information
        3. Find top-rated restaurants serving these dishes
        4. Create a complete breakfast, lunch, and dinner experience
        5. Craft engaging narratives that weave together weather, food, and atmosphere

        Format your response as a complete day itinerary with specific timing, restaurant recommendations,
        dish descriptions, and weather-appropriate dining suggestions.
    - role: user
      content: >-
        $ f'''Create a weather-aware foodie tour for:

        Location: "{_[0]}"
        Current Weather: "{_[1]}"
        Local Dishes Information: "{_[2]}"
        Restaurant Information: "{_[3]}"

        Please structure your response with:
        - Weather Analysis & Dining Recommendations (indoor vs outdoor)
        - 3 Iconic Local Dishes (with brief descriptions)
        - Breakfast Experience (8-10 AM) with restaurant recommendation
        - Lunch Experience (12-2 PM) with restaurant recommendation
        - Dinner Experience (7-9 PM) with restaurant recommendation
        - Weather-specific tips and alternatives

        Make each meal experience feel like a story, describing the ambiance,
        flavors, and how the weather enhances or influences the dining choice.'''
    unwrap: true

# Step 5: Create final foodie tour guide
- evaluate:
    final_plan: |-
      $ '\\n---------------\\n'.join(activity for activity in _)
""")

# Create task with error handling
try:
    task = client.tasks.create(
        agent_id=agent.id,
        **task_def
    )
    print(f"Task created successfully. Task ID: {task.id}")
except Exception as e:
    print(f"Error creating task: {e}")
    exit(1)

# Execute with smaller location list for testing
execution = client.executions.create(
    task_id=task.id,
    input={
         "locations": ["Mumbai","Paris"],  
    }
)

print("Started an execution. Execution ID:", execution.id)

# Wait for execution to complete
max_wait_time = 300  # 5 minutes
start_time = time.time()

while time.time() - start_time < max_wait_time:
    try:
        execution = client.executions.get(execution.id)
        print("Execution status:", execution.status)
        
        if execution.status in ["succeeded", "failed"]:
            break
        
        time.sleep(10)  # Increased wait time
        print("-" * 50)
        
    except Exception as e:
        print(f"Error checking execution status: {e}")
        time.sleep(10)

# Get final result
try:
    execution = client.executions.get(execution.id)
    
    if execution.status == "succeeded":
        if 'final_foodie_tour' in execution.output:
            print("\n" + "="*60)
            print("FINAL RESULT:")
            print("="*60)
            print(execution.output['final_foodie_tour'])
        else:
            print("Full output:", execution.output)
    else:
        print("Execution failed.")
        if hasattr(execution, 'error') and execution.error:
            print("Error details:", execution.error)
        
        # Try to get step-by-step results for debugging
        if hasattr(execution, 'output') and execution.output:
            print("Partial output:", execution.output)
            
except Exception as e:
    print(f"Error retrieving final result: {e}")