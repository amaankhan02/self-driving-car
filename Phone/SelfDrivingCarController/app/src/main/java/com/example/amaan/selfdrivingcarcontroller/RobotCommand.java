package com.example.amaan.selfdrivingcarcontroller;

/**
 * Created by amaan on 11/23/2017.
 */

public enum RobotCommand
{
    Speed("SS", "Speed", ButtonType.Value),
    SteerAngle("SA", "Steer Angle", ButtonType.Value),
    StartAutonomous("^", "Start Autonomous", ButtonType.Toggle),
    StopAutonomous("%", "Stop Autonomous", ButtonType.Toggle),
    Forward("FF", "Forward"),
    Back("BB", "Back"),
    Left("LL", "Left"),
    Right("RR", "Right"),
    ResetSteer("-", "Reset Steer", ButtonType.Toggle),
    AllMotorStop(",", "Stop ALL Motors", ButtonType.Toggle),
    StartTrainingSession(":", "Start Training Session", ButtonType.Toggle),  //Toggle button types DONT need a CommandState
    PauseTrainingSession("@", "Stop Training Session", ButtonType.Toggle),
    SaveTS("*", "Save Training Session"),
    DiscardTS("&", "Discard Training Session"); //discards the current TS

    private String commandCode;  //TODO: Understand how strings declaration in enum
    private String description;
    private ButtonType buttonType;
//    private String delimeter;

    RobotCommand(String commandCode, String description)
    {
        this.commandCode = commandCode;
        this.description = description;
        this.buttonType = buttonType.Touch;
//        this.delimeter = ";";
    }

    RobotCommand(String commandCode, String description, ButtonType buttonType)
    {
        this.commandCode = commandCode;
        this.description = description;
        this.buttonType = buttonType;  //TODO: I think should be buttonType.Value ?? --> NO, cause it can be .value or .toggle. It returns you the right one from parameter
    }

    public String getCommandCode()
    {
        return commandCode;
    }
    public String getDescription() { return description; }
    public ButtonType getButtonType() { return buttonType; }
}

