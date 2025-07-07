"""
Prompt variants for agerate YouTube channel age rating evaluation.
"""

VERSION_1 = """YouTube channel "{channel_name}" analysis:

CHANNEL INFO:
- Description: {description}
- Topics: {topics}
- Created: {created_year}
- Videos: {video_count}, Subscribers: {subscriber_count}

RECENT VIDEOS SAMPLE:
{video_sample}

Based on channel and actual video content, provide safety-focused parental guidance. Focus on content safety only (complexity doesn't matter).

Format:
- Minimum Age: [0-18]
- Content Categories: [2-4 specific categories like Gaming, Educational, Music, Comedy, etc.]
- Description: [Brief content overview and safety concerns based on actual videos]"""

PROMPTS = {
    "v1_baseline": VERSION_1,
    
    "v2_detailed": VERSION_1 + """

SAFETY ANALYSIS FRAMEWORK:
1. Language appropriateness (profanity, mature themes)
2. Visual content safety (violence, suggestive content)
3. Educational vs entertainment value
4. Potential psychological impact on young viewers
5. Community interaction risks

Provide detailed reasoning for age recommendation.""",

    "v3_concise": """Analyze YouTube channel "{channel_name}" for minimum safe viewing age (0-18).

Channel: {description}
Topics: {topics}
Sample videos: {video_sample}

Return only: Age number, 2-3 categories, brief safety note.""",

    "v4_structured": """YOUTUBE CHANNEL SAFETY ASSESSMENT

TARGET: {channel_name}
DATA: {description} | {topics} | {video_sample}
CONTENT FLAGS: {content_categories}
MATURITY SCORE: {maturity_score}

EVALUATION CRITERIA:
□ Language Safety (0-5 scale)
□ Content Appropriateness (0-5 scale)  
□ Educational Value (0-5 scale)
□ Risk Factors Present (Y/N)

OUTPUT:
Minimum Age: [NUMBER]
Categories: [LIST]
Safety Score: [0-25]
Reasoning: [BRIEF]""",

    "v5_examples": VERSION_1 + """

REFERENCE EXAMPLES:
- Cocomelon (Age 2): Simple songs, bright colors, no safety concerns
- MrBeast (Age 13): Challenges, mild language, intense competition
- PewDiePie (Age 16): Gaming, occasional strong language, mature humor
- Educational channels (Age 8+): Learning content, minimal risks

Use these as calibration for your assessment.""",

    "v6_chain_of_thought": """Let me analyze YouTube channel "{channel_name}" step by step for age appropriateness.

Channel Data: {description} | {topics} | {video_sample}

STEP 1: Content Theme Analysis
What is the primary content type?

STEP 2: Language Safety Check  
Are there profanity, mature themes, or inappropriate language?

STEP 3: Visual Content Review
Any violence, suggestive content, or disturbing imagery?

STEP 4: Target Audience Assessment
Who does this content seem designed for?

STEP 5: Risk Factor Evaluation
What could be concerning for younger viewers?

FINAL DETERMINATION:
Minimum Age: [0-18]
Categories: [2-4 categories]
Reasoning: [Based on above analysis]""",

    "v7_expert_persona": """As a child development expert and digital media safety consultant, I'm evaluating YouTube channel "{channel_name}" for age appropriateness.

Professional Assessment Framework:
Channel Profile: {description}
Content Categories: {topics}
Recent Content: {video_sample}

Drawing from child psychology research and digital media safety guidelines, I recommend:

Minimum Viewing Age: [0-18 years]
Content Classification: [Specific categories]
Professional Recommendation: [Evidence-based safety guidance]

This assessment considers developmental appropriateness, content safety standards, and potential impact on young viewers.""",

    "v8_minimal": """Channel: {channel_name}
Content: {topics}
Sample: {video_sample}

Age: [0-18]
Type: [categories]
Safe: [Y/N with reason]""",

    "v9_safety_first": VERSION_1 + """

PRIORITY: Child safety is paramount. Err on the side of caution.

RED FLAGS TO WATCH FOR:
- Inappropriate language or themes
- Violence or scary content
- Suggestive material
- Dangerous activities kids might imitate
- Toxic community behavior

If in doubt, recommend higher age.""",

    "v10_numeric_focus": VERSION_1 + """

IMPORTANT: Your age recommendation must be a single number between 0-18.
Examples: 3, 8, 13, 16

Consider these age milestones:
- 0-3: Toddler content only
- 4-7: Early childhood, simple themes
- 8-12: Middle childhood, more complex but safe
- 13-15: Teen content, some mature themes OK
- 16-18: Near-adult content acceptable""",

    "v11_enriched": """ENHANCED YOUTUBE CHANNEL ANALYSIS: {channel_name}

CONTENT INTELLIGENCE:
- Detected Categories: {content_categories}
- Maturity Score: {maturity_score}/10
- Safety Flags: Kid-Safe: {safety_flags[kid_safe]}, Age-Restricted: {safety_flags[age_restricted]}, Adult Content: {safety_flags[adult_content]}

CHANNEL DATA:
- Description: {description}
- Topics: {topics}
- Recent Videos: {video_sample}

SMART RECOMMENDATION:
Based on automated content analysis and safety flags, determine the minimum appropriate age (0-18).""",

    "v12_criteria_based": """CONTENT CRITERIA ASSESSMENT: {channel_name}

AUTO-DETECTED CONTENT: {content_categories}
RISK SCORE: {maturity_score} (higher = more mature)

EVALUATION LOGIC:
• If "Made for Kids" detected → Age 3-5
• If "Educational" content → Age 8+
• If "Adult Content" or "Drama/Controversy" → Age 18
• If "Mature Gaming" or "Mature Language" → Age 17
• Default fallback → Age 13

CHANNEL CONTEXT: {description}
SAMPLE CONTENT: {video_sample}

Apply criteria-based logic with contextual adjustment.""",

    "v13_token_optimized": """Channel: {channel_name}
Flags: {content_categories}
Score: {maturity_score}
Kids: {safety_flags[kid_safe]} | Adult: {safety_flags[adult_content]}

Age [0-18]: __"""
}