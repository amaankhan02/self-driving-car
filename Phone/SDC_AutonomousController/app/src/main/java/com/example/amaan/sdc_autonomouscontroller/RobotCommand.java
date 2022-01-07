package com.example.amaan.sdc_autonomouscontroller;

/**
 * Maps server robot commands to enums
 */

public enum RobotCommand
{
    Speed("SS", "Speed", ButtonType.Value),
    StartAutonomous("^", "Start Autonomous", ButtonType.Toggle),
    StopAutonomous("%", "Stop Autonomous", ButtonType.Toggle);


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
