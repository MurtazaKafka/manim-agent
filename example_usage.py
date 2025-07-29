#!/usr/bin/env python3
"""
Example usage of the Manim Explainer Agent system
"""

import asyncio
from manim_agent import ManimExplainerAgent


async def main():
    # Create the main agent
    agent = ManimExplainerAgent()
    
    # Example requests
    requests = [
        "Explain the Taylor series with visual examples",
        "Show how derivatives work",
        "Visualize the Pythagorean theorem"
    ]
    
    for request in requests:
        print(f"\n{'='*60}")
        print(f"Processing: {request}")
        print(f"{'='*60}")
        
        # Generate Manim code
        manim_code = await agent.create_video(request)
        
        if manim_code:
            # Save the generated code
            filename = request.lower().replace(" ", "_")[:30] + ".py"
            with open(f"generated_{filename}", "w") as f:
                f.write(manim_code)
            
            print(f"Generated Manim code saved to: generated_{filename}")
            print("\nTo render the video, run:")
            print(f"  manim -pql generated_{filename}")
        else:
            print("Failed to generate Manim code")


if __name__ == "__main__":
    asyncio.run(main())