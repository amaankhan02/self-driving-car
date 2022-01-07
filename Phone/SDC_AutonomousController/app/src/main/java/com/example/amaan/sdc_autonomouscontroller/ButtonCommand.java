package com.example.amaan.sdc_autonomouscontroller;

/**
 * Created by amaan on 11/18/2017.
 */

public class ButtonCommand
{
    private final RobotCommand robotCommand;
//    private CommandState commandState;

    private final int value;

    ButtonCommand(RobotCommand robotCommand)
    {
        this.robotCommand = robotCommand;
        value = 0;
    }

    ButtonCommand(RobotCommand robotCommand, int value)
    {
        this.robotCommand = robotCommand;
        this.value = value;
    }

//    public void setCommandState(CommandState commandState) { this.commandState = commandState; }
    public RobotCommand getRobotCommand() { return robotCommand;}
//    public CommandState getCommandState() {return this.commandState;}

    /**
     * Build a single string to be sent as a command which combines code and delimeter
     * @return The command
     */
    public String command()
    {
        String command = robotCommand.getCommandCode();  //Get the command of the robotCommand that was initialized. ex: "FF"", ""LL", etc
//        switch(robotCommand.getButtonType())
//        {
//            case Touch:
//                command += commandState.getCommand();  //Adds the "+" or "-" to command string to indicate if it is moving or stopped
//                break;
//            case Value:
//                command += Integer.toString(value);   //Adds the speed variable to command string to incdicate the speed
//                break;
//            default:
//                break;
//        }
        if(robotCommand.getButtonType()==ButtonType.Value)  //Checks if it is a Speed Robot Command
            command += Integer.toString(value);
        command += ";"; // Add a delimeter
        return command;
    }
}

