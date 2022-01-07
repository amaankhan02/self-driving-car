package com.example.amaan.selfdrivingcarcontroller;

import android.app.Activity;

/**
 * Created by amaan on 11/23/2017.
 */

public class Sender
{
    private ISocketClientThread mainActivity;

    public Sender(ISocketClientThread activity)
    {
        this.mainActivity = activity;
    }

    public void sendButtonCommand(ButtonCommand bc)
    {
        mainActivity.getSocketClientThread().sendCommand(bc);

    }
}