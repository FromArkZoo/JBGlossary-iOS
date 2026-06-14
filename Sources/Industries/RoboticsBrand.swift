import SwiftUI

let roboticsBrand = Brand(
    appStoreName: "JB Robotics",
    displayName: "JB Robotics",
    navigationTitle: "JB Robotics",
    titlePrefix: "JB",
    titleBody: "Robotics",
    subtitle: "decoding robots & autonomy",
    tagline: nil,
    entryNoun: "entries",
    dataResource: "glossary_robotics",
    primaryColor: Color(red: 0.878, green: 0.416, blue: 0.106),       // #E06A1B signal amber
    primaryDarkColor: Color(red: 0.710, green: 0.325, blue: 0.059),   // #B5530F deeper amber
    bgColor: PGColors.bg,
    urlScheme: "robotics",
    aboutParagraphs: [
        "JB Robotics is a generalist's reference for the language of robots, autonomy, and embodied AI — the jargon you meet in the humanoid race, self-driving news, factory-automation pitches, and robotics research. It spans the robot itself (mechanics, actuators, kinematics), the autonomy stack (sensing, perception, control, planning, and the learning that now drives physical action), and the deployed world: autonomous vehicles, drones, the factory floor, and the companies building it.",
        "Entries summarise publicly available material from robotics standards bodies, research labs, open-source projects, and platform makers. They are written for orientation in plain English, not as engineering, safety, or investment guidance."
    ],
    aboutDisclaimer: "Educational reference. Not engineering, safety, or investment advice.",
    aboutSources: [
        BrandSource(
            heading: "Standards & government",
            items: ["IEEE RAS", "NIST", "ISO", "SAE International", "FAA"]
        ),
        BrandSource(
            heading: "Software & platforms",
            items: ["ROS", "Open Robotics", "MoveIt", "Gazebo", "NVIDIA Isaac"]
        ),
        BrandSource(
            heading: "Research & industry",
            items: ["arXiv", "DARPA", "NASA", "IFR"]
        ),
        BrandSource(
            heading: "Makers",
            items: ["Boston Dynamics"]
        )
    ],
    lenses: [
        LensConfig(
            id: "basics",
            glyph: "B",
            title: "Basics",
            subtitle: "Foundational robotics vocabulary",
            kind: .allowlist([
                // Concepts
                "Robot", "Robotics", "Embodied intelligence", "Autonomy",
                "Levels of autonomy", "End-effector", "Mapping", "Kinematics",
                "Dynamics", "Compliance", "Dexterity", "Navigation",
                "Trajectory", "Actuation", "Sensing", "Real-time",
                "Robustness", "Accuracy", "Human-robot interaction", "Swarm robotics",
                "Agent", "Robot Operating System", "Simulation", "Reward",
                "Foundation model", "Collision avoidance", "Task", "Soft robotics",
                "Uncanny valley", "Haptics", "Tactile sensing", "Vision",
                "Mechatronics", "Servomechanism", "Automation", "Robotics-as-a-service",
                "Fleet", "Safety", "Self-driving", "Drone",
                "Moravec's paradox", "Three Laws of Robotics", "Android", "Service robotics",
                "Industrial robotics", "Dull, dirty, dangerous",
                // Mechanics & Structures
                "Degrees of freedom", "Workspace", "Kinematic chain", "Link",
                "Joint", "Revolute joint", "Prismatic joint", "Chassis",
                "Reach", "Backlash", "Stiffness",
                // Actuation & Drives
                "Actuator", "Electric motor", "DC motor", "Brushless DC motor",
                "Stepper motor", "Servomotor", "Linear actuator", "Gearbox",
                "Hydraulic actuator", "Pneumatic actuator", "Pulse-width modulation", "Encoder",
                // Kinematics & Dynamics
                "Pose", "Forward kinematics", "Inverse kinematics", "Quaternion",
                "Jacobian matrix", "Center of mass", "Zero moment point",
                // Power & Compute
                "Latency", "Edge computing", "Graphics processing unit", "Microcontroller",
                "Embedded system", "Lithium-ion battery",
                // Locomotion
                "Locomotion", "Odometry", "Legged locomotion", "Bipedal locomotion",
                "Quadrupedal locomotion", "Gait", "Wheeled locomotion", "Differential drive",
                // Manipulation
                "Manipulator", "Manipulation", "Grasping", "Gripper",
                "Parallel-jaw gripper", "Robotic hand", "Pick and place", "Pose estimation",
                // Form Factors
                "Autonomous mobile robot", "Automated guided vehicle", "Humanoid robot", "Quadruped robot",
                "Wheeled robot", "Articulated robot", "Cobot", "Mobile manipulator",
                "Unmanned aerial vehicle", "Multirotor drone", "Exoskeleton", "Surgical robot",
                "Self-driving car", "Robotaxi",
                // Sensing
                "Proprioception", "Sensor fusion", "Calibration", "Sensor",
                "Inertial measurement unit", "Accelerometer", "Gyroscope", "Camera",
                "Stereo camera", "Depth camera", "LiDAR", "Point cloud",
                "Radar", "Global Navigation Satellite System", "Field of view",
                // Perception
                "State estimation", "Localization", "Perception", "Occupancy grid",
                "Computer vision", "SLAM", "Kalman filter", "Object detection",
                "Obstacle detection", "HD map",
                // Control
                "Control loop", "Force control", "Impedance control", "Feedback control",
                "PID controller", "Setpoint", "Gain", "Model predictive control",
                "Position control", "Torque control",
                // Planning & Navigation
                "Motion planning", "Obstacle avoidance", "Waypoint", "Behavior tree",
                "Path planning", "A* search", "Rapidly-exploring random tree",
                // Software & Simulation
                "Digital twin", "Sim-to-real", "ROS", "ROS 2",
                "URDF", "Gazebo", "Physics engine",
                // Learning & Embodied AI
                "Embodiment", "World model", "Teleoperation", "Policy",
                "Reinforcement learning", "Imitation learning", "Generalization", "Vision-language-action model",
                "Sim-to-real transfer", "Robot foundation model", "Embodied AI", "Reward function",
                "Neural network", "Transformer",
                // Autonomous Vehicles
                "Edge case", "Operational design domain", "Functional safety", "Autonomous vehicle",
                "SAE levels of driving automation", "Advanced driver-assistance systems", "Adaptive cruise control", "Automatic emergency braking",
                // Aerial & Drones
                "Quadcopter", "eVTOL", "Autopilot", "Propeller",
                "Drone delivery",
                // Industrial Automation
                "Collaborative robot", "Industry 4.0", "Industrial automation", "Programmable logic controller",
                "Teach pendant", "End-of-arm tooling", "Computer numerical control", "Machine vision",
                // Safety & Standards
                "Emergency stop", "ISO 26262",
                // Companies & Platforms
                "Boston Dynamics", "Spot", "Tesla Optimus", "Waymo",
                "DJI", "iRobot",
                // Industry & Deployment
                "Human-in-the-loop", "Total cost of ownership", "Return on investment",
            ])
        ),
        LensConfig(
            id: "robot",
            glyph: "R",
            title: "The Robot",
            subtitle: "Body, motion & power",
            kind: .categoryFilter(
                categories: [
                    "Mechanics & Structures", "Actuation & Drives",
                    "Kinematics & Dynamics", "Power & Compute",
                    "Locomotion", "Manipulation", "Form Factors"
                ],
                excludedTerms: []
            )
        ),
        LensConfig(
            id: "senseControl",
            glyph: "S",
            title: "Sense & Control",
            subtitle: "The perception–action stack",
            kind: .categoryFilter(
                categories: [
                    "Sensing", "Perception", "Control",
                    "Planning & Navigation", "Software & Simulation"
                ],
                excludedTerms: []
            )
        ),
        LensConfig(
            id: "embodiedAI",
            glyph: "E",
            title: "Embodied AI",
            subtitle: "Learning that drives physical action",
            kind: .categoryFilter(
                categories: ["Learning & Embodied AI"],
                excludedTerms: []
            )
        ),
        LensConfig(
            id: "systems",
            glyph: "I",
            title: "Systems & Industry",
            subtitle: "The deployed world",
            kind: .categoryFilter(
                categories: [
                    "Autonomous Vehicles", "Aerial & Drones",
                    "Industrial Automation", "Safety & Standards",
                    "Companies & Platforms", "Industry & Deployment"
                ],
                excludedTerms: []
            )
        )
    ],
    accentTint: nil,
    sourceURLs: [
        // Standards & government
        "IEEE RAS":         URL(string: "https://www.ieee-ras.org")!,
        "IEEE":             URL(string: "https://www.ieee.org")!,
        "NIST":             URL(string: "https://www.nist.gov")!,
        "ISO":              URL(string: "https://www.iso.org")!,
        "SAE International": URL(string: "https://www.sae.org")!,
        "SAE":              URL(string: "https://www.sae.org")!,
        "FAA":              URL(string: "https://www.faa.gov")!,
        // Software & platforms
        "ROS":              URL(string: "https://www.ros.org")!,
        "Open Robotics":    URL(string: "https://www.openrobotics.org")!,
        "MoveIt":           URL(string: "https://moveit.ai")!,
        "Gazebo":           URL(string: "https://gazebosim.org")!,
        "NVIDIA Isaac":     URL(string: "https://developer.nvidia.com/isaac")!,
        "NVIDIA":           URL(string: "https://www.nvidia.com")!,
        // Research & industry
        "arXiv":            URL(string: "https://arxiv.org/list/cs.RO/recent")!,
        "DARPA":            URL(string: "https://www.darpa.mil")!,
        "NASA":             URL(string: "https://www.nasa.gov")!,
        "IFR":              URL(string: "https://ifr.org")!,
        // Makers
        "Boston Dynamics":  URL(string: "https://www.bostondynamics.com")!
    ]
)
