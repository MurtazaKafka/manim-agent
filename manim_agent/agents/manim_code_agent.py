from ..core.base_agent import BaseAgent, AgentMessage
import asyncio


class ManimCodeAgent(BaseAgent):
    """Agent responsible for generating Manim animation code"""
    
    async def process(self, message: AgentMessage) -> AgentMessage:
        """Process code generation requests"""
        # First simulate (following CLAUDE.md)
        simulation = self.simulate_algorithm("Generate Manim code")
        
        if message.action == "generate_code":
            content = message.payload.get("content", {})
            topic = message.payload.get("topic", "")
            
            # Generate Manim code based on content
            manim_code = self._generate_manim_code(content, topic)
            
            return AgentMessage(
                sender=self.name,
                recipient=message.sender,
                action="code_ready",
                payload={"code": manim_code}
            )
        
        return message
    
    def _generate_manim_code(self, content: dict, topic: str) -> str:
        """Generate Manim scene code"""
        if "taylor series" in topic.lower():
            return '''from manim import *
import numpy as np

class TaylorSeriesExplainer(Scene):
    def construct(self):
        # Title
        title = Text("Taylor Series", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))
        
        # Mathematical definition
        formula = MathTex(
            r"f(x) = f(a) + f'(a)(x-a) + \\frac{f''(a)}{2!}(x-a)^2 + ..."
        )
        self.play(Write(formula))
        self.wait(2)
        
        # Visual example with sin(x)
        self.play(FadeOut(formula))
        
        # Create axes
        axes = Axes(
            x_range=[-PI, PI, PI/2],
            y_range=[-2, 2, 0.5],
            axis_config={"color": BLUE},
        )
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")
        
        # Original function
        sin_graph = axes.plot(lambda x: np.sin(x), color=GREEN)
        sin_label = Text("sin(x)", color=GREEN).next_to(sin_graph, UP)
        
        self.play(Create(axes), Write(axes_labels))
        self.play(Create(sin_graph), Write(sin_label))
        self.wait(1)
        
        # Taylor approximations
        taylor_1 = axes.plot(lambda x: x, color=YELLOW)
        taylor_3 = axes.plot(lambda x: x - x**3/6, color=ORANGE)
        taylor_5 = axes.plot(lambda x: x - x**3/6 + x**5/120, color=RED)
        
        self.play(Create(taylor_1))
        self.wait(1)
        self.play(Transform(taylor_1, taylor_3))
        self.wait(1)
        self.play(Transform(taylor_1, taylor_5))
        self.wait(2)
        
        # Conclusion
        conclusion = Text(
            "Taylor series provide polynomial approximations of functions",
            font_size=24
        ).to_edge(DOWN)
        self.play(Write(conclusion))
        self.wait(2)
'''
        
        # Default template for other topics
        return f'''from manim import *

class {topic.replace(" ", "")}Explainer(Scene):
    def construct(self):
        title = Text("{content.get('title', topic)}", font_size=48)
        self.play(Write(title))
        self.wait(2)
        
        # Add more animations based on content sections
        for section in {content.get('sections', [])}:
            text = Text(section.get('content', ''), font_size=24)
            self.play(Write(text))
            self.wait(2)
            self.play(FadeOut(text))
'''