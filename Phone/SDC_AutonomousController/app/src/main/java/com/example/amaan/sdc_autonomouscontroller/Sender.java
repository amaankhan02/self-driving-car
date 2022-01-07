package com.example.amaan.sdc_autonomouscontroller;

/**
 * Created by amaan on 11/18/2017.
 */

public class Sender
{
    private MainActivity mainActivity;

    public Sender(MainActivity aca)
    {
        this.mainActivity = aca;
    }

    public void sendButtonCommand(ButtonCommand bc)
    {
        mainActivity.getSocketClientThread().sendCommand(bc);
    }
}