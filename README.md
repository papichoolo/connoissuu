# Connoissuu 🍽️

**An AI-Powered Weather-Aware Foodie Tour Guide**

This project is an assignment submission for a Founder's Office role that demonstrates building a real AI workflow with Julep. Connoissuu creates personalized one-day culinary experiences by combining weather data, local cuisine knowledge, and restaurant recommendations.

## 🎯 Project Overview

Connoissuu generates delightful foodie tours for any city by:
- Analyzing current weather conditions to suggest indoor/outdoor dining
- Identifying 3 iconic local dishes per city
- Finding top-rated restaurants serving these dishes
- Creating weather-aware breakfast, lunch, and dinner experiences
- Generating a beautifully formatted PDF tour guide

## 🏗️ Architecture & Workflow

### Core Components

1. **Julep AI Agent**: Claude-3.5-Sonnet powered food tour guide
2. **Weather Integration**: OpenWeatherMap API for real-time conditions
3. **Search Engine**: Brave Search API for restaurant and cuisine data
4. **PDF Generation**: Custom-formatted tour guide creation

### Workflow Steps

```
Input: List of Cities
    ↓
Step 0: Fetch Weather Data
    ↓ (Parallel Processing)
Step 1: Search Iconic Local Dishes
    ↓ (Parallel Processing)  
Step 2: Search Top-Rated Restaurants
    ↓
Step 3: Data Aggregation (Zip locations, weather, dishes, restaurants)
    ↓
Step 4: AI-Generated Tour Itineraries (Parallel processing with max 3 concurrent)
    ↓
Step 5: Final Compilation & PDF Generation
```

### Key Features

- **Weather-Aware Recommendations**: Indoor vs outdoor dining based on conditions
- **Local Cuisine Focus**: Authentic dishes specific to each location
- **Complete Day Planning**: Structured breakfast, lunch, and dinner experiences
- **Narrative Storytelling**: Engaging descriptions of ambiance and flavors
- **Professional PDF Output**: Beautifully formatted tour guide document

## 🛠️ Technical Implementation

### Dependencies

```
pip install -r requirements.txt
```

## 📖 Usage

1. **Interactive City Input**
   ```
   Enter a city to create a foodie tour (or type 'done' to finish): Paris
   Enter a city to create a foodie tour (or type 'done' to finish): Tokyo
   Enter a city to create a foodie tour (or type 'done' to finish): done
   ```

2. **Automatic Processing**
   - Weather data fetched for each city
   - Local cuisine research conducted
   - Restaurant recommendations gathered
   - AI generates personalized itineraries

3. **Output Generation**
   - Console display of complete tour guide
   - PDF file saved locally (`foodie_tour_guide.pdf`)
   - File uploaded to Julep platform

## 📋 Sample Output Structure

For each city, the generated tour includes:

```
CITY NAME
├── Weather Analysis & Dining Recommendations
├── 3 Iconic Local Dishes (with descriptions)
├── Breakfast Experience (8-10 AM)
│   ├── Restaurant recommendation
│   └── Ambiance & flavor narrative
├── Lunch Experience (12-2 PM)
│   ├── Restaurant recommendation
│   └── Weather-appropriate suggestions
├── Dinner Experience (7-9 PM)
│   ├── Restaurant recommendation
│   └── Atmospheric descriptions
└── Weather-Specific Tips & Alternatives
```

## 🎨 PDF Formatting Features

- **Professional Layout**: Custom headers, footers, and page numbering
- **Color-Coded Sections**: Different colors for headings, restaurants, and content
- **Smart Text Wrapping**: Automatic line breaks for readability
- **Section Separation**: Clear visual dividers between cities
- **Typography Hierarchy**: Distinct font sizes and styles for different content types

## 🔧 Technical Highlights

### Parallel Processing
- Weather, dishes, and restaurant searches run concurrently
- Tour generation supports up to 3 parallel city processing
- Optimized execution time for multiple cities
