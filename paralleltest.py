from julep import Client
import os
from dotenv import load_dotenv
import time
import yaml
from fpdf import FPDF

load_dotenv(override=True)
JULEP_API_KEY = os.environ["JULEP_API_KEY"]
BRAVE_API_KEY = os.environ["BRAVE_API_KEY"]
WEATHER_API_KEY = os.environ["OPENWEATHERMAP_API_KEY"]

# Create a Julep client
client = Client(api_key=JULEP_API_KEY, environment="production")

agent = client.agents.create(
    name="Foodie Tour Guide",
    model="claude-3.5-sonnet-20241022",
    about="An expert food tour guide that creates weather-aware culinary experiences."
)




task_def = yaml.safe_load(f"""
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
      openweathermap_api_key: "{WEATHER_API_KEY}"

- name: internet_search
  type: integration
  integration:
    provider: brave
    setup:
      brave_api_key: "{BRAVE_API_KEY}"

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

        Location: "{{_[0]}}"
        Current Weather: "{{_[1]}}"
        Local Dishes Information: "{{_[2]}}"
        Restaurant Information: "{{_[3]}}"

        Please structure your response with:
        - Weather Analysis & Dining Recommendations (indoor vs outdoor)
        - 3 Iconic Local Dishes (with brief descriptions)
        - Breakfast Experience (8-10 AM) with restaurant recommendation
        - Lunch Experience (12-2 PM) with restaurant recommendation
        - Dinner Experience (7-9 PM) with restaurant recommendation
        - Weather-specific tips and alternatives

        Make each meal experience feel like a story, describing the ambiance,
        flavors, and how the weather enhances or influences the dining choice. Also PLEASE TRY TO NOT USE ACCENTED CHARACTERS IN THE OUTPUT.'''
    unwrap: true

# Step 5: Create final foodie tour guide
- evaluate:
    final_plan: |-
      $ '\\n---------------\\n'.join(activity for activity in _)
""")

cities=[]
#take user input for cities
while True:
    city = input("Enter a city to create a foodie tour (or type 'done' to finish [WARNING: ENTER REAL CITIES/LOCATIONS]): ")
    if city.lower() == 'done':
        break
    cities.append(city)
# Create task with error handling
try:
    task = client.tasks.create(
        name="Foodie Tour Guide",
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
         "locations": cities,
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


try:
    execution = client.executions.get(execution.id)
    
    if execution.status == "succeeded":
        if 'final_plan' in execution.output:
            print("\n" + "="*60)
            print("FINAL RESULT:")
            print("="*60)
            print(execution.output['final_plan'])
            
            # Create beautiful PDF file
            from fpdf import FPDF, XPos, YPos
            import base64
            import re
            
            local_filename = "foodie_tour_guide.pdf"
            
            class BeautifulPDF(FPDF):
                def header(self):
                    # Add logo or header styling
                    self.set_font('Helvetica', 'B', 20)
                    self.set_text_color(41, 128, 185)  # Nice blue color
                    self.cell(0, 15, 'Connoissuu Guide', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                    self.set_text_color(0, 0, 0)  # Reset to black
                    self.ln(10)
                
                def footer(self):
                    self.set_y(-15)
                    self.set_font('Helvetica', 'I', 8)
                    self.set_text_color(128, 128, 128)
                    self.cell(0, 10, f'Page {self.page_no()}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
            
            # Create PDF instance
            pdf = BeautifulPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Process content
            content = execution.output['final_plan']
            sections = content.split('---------------')
            
            for i, section in enumerate(sections):
                if section.strip():
                    lines = section.strip().split('\n')
                    
                    # Process each line with better formatting
                    for line_num, line in enumerate(lines):
                        line = line.strip()
                        if not line:
                            pdf.ln(3)
                            continue
                        
                        # Detect headings (lines that end with colons or are in all caps)
                        if (line.endswith(':') and len(line) < 60) or (line.isupper() and len(line) < 80):
                            pdf.set_font('Helvetica', 'B', 14)
                            pdf.set_text_color(52, 73, 94)  # Dark blue-gray
                            pdf.ln(5)
                            pdf.cell(0, 8, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
                            pdf.ln(3)
                        
                        # Detect sub-headings (lines with specific patterns)
                        elif re.match(r'^(Weather Analysis|Breakfast|Lunch|Dinner|Tips|Alternative)', line, re.IGNORECASE):
                            pdf.set_font('Helvetica', 'B', 12)
                            pdf.set_text_color(231, 76, 60)  # Red accent
                            pdf.ln(3)
                            pdf.cell(0, 7, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
                            pdf.ln(2)
                        
                        # Detect restaurant names or venues (lines with specific patterns)
                        elif re.match(r'^(Venue:|Experience \()', line):
                            pdf.set_font('Helvetica', 'B', 11)
                            pdf.set_text_color(39, 174, 96)  # Green accent
                            pdf.cell(0, 6, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
                            pdf.ln(1)
                        
                        # Regular content
                        else:
                            pdf.set_font('Helvetica', '', 10)
                            pdf.set_text_color(0, 0, 0)  # Black
                            
                            # Handle long lines with word wrapping
                            if len(line) > 85:
                                words = line.split(' ')
                                current_line = ""
                                
                                for word in words:
                                    if len(current_line + word + " ") <= 85:
                                        current_line += word + " "
                                    else:
                                        if current_line.strip():
                                            pdf.cell(0, 5, current_line.strip(), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
                                        current_line = word + " "
                                
                                if current_line.strip():
                                    pdf.cell(0, 5, current_line.strip(), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
                            else:
                                pdf.cell(0, 5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
                            
                            pdf.ln(1)
                    
                    # Add separator between sections
                    if i < len(sections) - 1:
                        pdf.ln(10)
                        pdf.set_draw_color(189, 195, 199)  # Light gray
                        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
                        pdf.ln(10)
            
            # Save PDF
            pdf.output(local_filename)
            print(f"local PDF file created: {local_filename}")
            
            # Read and encode PDF for Julep
            with open(local_filename, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
                pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            
            # Create file in Julep
            file = client.files.create(name="foodie_tour_guide.pdf", content=pdf_base64)
            print("PDF uploaded to Julep successfully. File ID:", file.id)
            
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
    print(f"An error occurred: {str(e)}")
    import traceback
    traceback.print_exc()


