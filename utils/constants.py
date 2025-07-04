from sentence_transformers import SentenceTransformer


class Constants:
    # DIRECTORIES
    ARTICLES_DIR = "wikipedia_articles/"
    VECTOR_CHUNKS = "data/chunks.pkl"

    # EVALUATION
    QUERIES = {
        "What is acceleration and how is it measured?": ["Acceleration"],
        "How does angular acceleration affect rotating objects?": ["Angular_acceleration", "Angular_velocity", "Rotation"],
        "What determines angular frequency in oscillations?": ["Angular_frequency", "Harmonic_oscillator", "Frequency"],
        "Explain the concept of angular momentum in physics.": ["Angular_momentum", "Moment_of_inertia", "Torque"],
        "How is angular velocity different from linear velocity?": ["Angular_velocity", "Velocity", "Motion"],
        "What defines the center of mass in a system?": ["Center_of_mass", "Mass", "Motion"],
        "What is centrifugal force and when does it occur?": ["Centrifugal_force", "Circular_motion", "Centripetal_force"],
        "Explain the effects of centripetal force on circular motion.": ["Centripetal_force", "Circular_motion", "Force"],
        "How does circular motion work in physics?": ["Circular_motion", "Force", "Angular_velocity"],
        "What causes the Coriolis force and how does it affect motion?": ["Coriolis_force", "Rotation", "Motion"],
        "What are the equations of motion for uniformly accelerated bodies?": ["Equations_of_motion", "Acceleration", "Newton%27s_laws_of_motion"],
        "Define force and its role in mechanics.": ["Force", "Newton%27s_laws_of_motion", "Momentum"],
        "How is frequency related to oscillations and waves?": ["Frequency", "Harmonic_oscillator", "Angular_frequency"],
        "What is a harmonic oscillator and its properties?": ["Harmonic_oscillator", "Frequency", "Equations_of_motion"],
        "Explain the concept of jerk in physics.": ["Jerk_(physics)", "Acceleration", "Motion"],
        "What factors affect the mass of an object?": ["Mass", "Center_of_mass", "Moment_of_inertia"],
        "How is moment of inertia calculated for different bodies?": ["Moment_of_inertia", "Rotation", "Mass"],
        "What is momentum and how is it conserved?": ["Momentum", "Newton%27s_laws_of_motion", "Force"],
        "Explain the principles of motion in classical mechanics.": ["Motion", "Newton%27s_laws_of_motion", "Equations_of_motion"],
        "What are Newton's laws of motion and their applications?": ["Newton%27s_laws_of_motion", "Force", "Momentum"],
        "How does rotation affect the dynamics of a body?": ["Rotation", "Angular_velocity", "Torque"],
        "What defines speed and how is it different from velocity?": ["Speed", "Velocity", "Motion"],
        "Explain torque and its effect on rotational motion.": ["Torque", "Rotation", "Moment_of_inertia"],
        "How is velocity defined in physics?": ["Velocity", "Motion", "Acceleration"],
        "What is work in physics and how is it calculated?": ["Work_(physics)", "Force", "Energy"],
    }

    # EMBEDDERS
    MPNET = "HuggingFace - MPNet"
    MINI_LM = "HuggingFace - MiniLM"
    ROBERTA = "HuggingFace - DistilRoBERTa"
    EMBEDDERS = {
        MINI_LM: SentenceTransformer("all-MiniLM-L6-v2"),
        MPNET: SentenceTransformer("all-mpnet-base-v2"),
        ROBERTA: SentenceTransformer("all-distilroberta-v1")
    }

    # ENVIRONMENT VARIABLE NAMES
    OLLAMA_URL = 'OLLAMA_URL'
    LLM_NAME = 'LLM_NAME'

    # LLM EVALUATION SET
    LLM_EVAL = [
        {
            "query": "What is the formula for acceleration?",
            "answer": r"a = \frac{\Delta v}{\Delta t}",
            "verbal": "acceleration equals change in velocity divided by change in time"
        },
        {
            "query": "State Newton's second law of motion.",
            "answer": r"F = m a",
            "verbal": "force equals mass times acceleration"
        },
        {
            "query": "Write the equation for angular momentum.",
            "answer": r"\mathbf{L} = \mathbf{r} \times \mathbf{p}",
            "verbal": "angular momentum equals position vector cross momentum"
        },
        {
            "query": "What is the formula for centripetal force?",
            "answer": r"F = m \frac{v^2}{r}",
            "verbal": "centripetal force equals mass times velocity squared divided by radius"
        },
        {
            "query": "Give the equation for kinetic energy.",
            "answer": r"E_k = \frac{1}{2} m v^2",
            "verbal": "kinetic energy equals one half mass times velocity squared"
        },
        {
            "query": "What is the work done by a constant force?",
            "answer": r"W = \mathbf{F} \cdot \mathbf{d}",
            "verbal": "work equals force dot displacement"
        },
        {
            "query": "State the formula for angular velocity.",
            "answer": r"\omega = \frac{\Delta \theta}{\Delta t}",
            "verbal": "angular velocity equals change in angle divided by change in time"
        },
        {
            "query": "What is the equation for frequency?",
            "answer": r"f = \frac{1}{T}",
            "verbal": "frequency equals one divided by period"
        },
        {
            "query": "Write the formula for momentum.",
            "answer": r"\mathbf{p} = m \mathbf{v}",
            "verbal": "momentum equals mass times velocity"
        },
        {
            "query": "What is the equation for gravitational force?",
            "answer": r"F = G \frac{m_1 m_2}{r^2}",
            "verbal": "gravitational force equals G times mass one times mass two divided by distance squared"
        },
        {
            "query": "State the equation for potential energy near Earth's surface.",
            "answer": r"E_p = mgh",
            "verbal": "potential energy equals mass times gravity times height"
        },
        {
            "query": "What is the formula for torque?",
            "answer": r"\tau = r F \sin \theta",
            "verbal": "torque equals radius times force times sine of angle"
        },
        {
            "query": "Write the equation for power in terms of work.",
            "answer": r"P = \frac{W}{t}",
            "verbal": "power equals work divided by time"
        },
        {
            "query": "What is the equation for Hooke's law?",
            "answer": r"F = -k x",
            "verbal": "force equals negative spring constant times displacement"
        },
        {
            "query": "State the equation for Ohm's law.",
            "answer": r"V = I R",
            "verbal": "voltage equals current times resistance"
        },
        {
            "query": "What is the equation for wave speed?",
            "answer": r"v = f \lambda",
            "verbal": "wave speed equals frequency times wavelength"
        },
        {
            "query": "Write the equation for the period of a pendulum.",
            "answer": r"T = 2\pi \sqrt{\frac{l}{g}}",
            "verbal": "period equals two pi times the square root of length divided by gravity"
        },
        {
            "query": "What is the equation for pressure?",
            "answer": r"P = \frac{F}{A}",
            "verbal": "pressure equals force divided by area"
        },
        {
            "query": "State the equation for density.",
            "answer": r"\rho = \frac{m}{V}",
            "verbal": "density equals mass divided by volume"
        },
        {
            "query": "What is the equation for impulse?",
            "answer": r"J = F \Delta t",
            "verbal": "impulse equals force times change in time"
        },
        {
            "query": "Write the equation for mechanical advantage.",
            "answer": r"MA = \frac{F_{out}}{F_{in}}",
            "verbal": "mechanical advantage equals output force divided by input force"
        },
        {
            "query": "What is the equation for centripetal acceleration?",
            "answer": r"a_c = \frac{v^2}{r}",
            "verbal": "centripetal acceleration equals velocity squared divided by radius"
        },
        {
            "query": "State the equation for elastic potential energy.",
            "answer": r"E = \frac{1}{2} k x^2",
            "verbal": "elastic potential energy equals one half spring constant times displacement squared"
        },
        {
            "query": "What is the equation for average speed?",
            "answer": r"v_{avg} = \frac{d}{t}",
            "verbal": "average speed equals distance divided by time"
        },
        {
            "query": "Write the equation for the area of a circle.",
            "answer": r"A = \pi r^2",
            "verbal": "area equals pi times radius squared"
        },
        {
            "query": "What is the equation for the circumference of a circle?",
            "answer": r"C = 2\pi r",
            "verbal": "circumference equals two pi times radius"
        },
        {
            "query": "State the equation for the volume of a sphere.",
            "answer": r"V = \frac{4}{3} \pi r^3",
            "verbal": "volume equals four thirds pi times radius cubed"
        },
    ]
