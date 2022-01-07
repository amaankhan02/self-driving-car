package com.example.amaan.selfdrivingcarcontroller;

import android.os.Handler;

/**
 * Created by amaan on 11/23/2017.
 */

public interface ISocketClientThread
{
    public final static int CONNECTION_ERROR = 0;
    public final static int CONNECTION_LOST = 1;

    public Handler getHandler();
    public SocketClientThread getSocketClientThread();
}
