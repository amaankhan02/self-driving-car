package com.example.amaan.selfdrivingcarcontroller;

import android.app.Activity;
import android.os.Handler;
import android.os.Message;
import android.util.Log;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.Socket;

/**
 * Created by amaan on 11/23/2017.
 */

public class SocketClientThread extends Thread
{
    private String host;
    private int port;
    private ISocketClientThread mainActivity;

    // Lock object used for thread synchronization
    private final Object lock = new Object();
    private boolean running = true;

    // Current command to send to arm
    private ButtonCommand buttonCommand;

    // The socket to the arm
    private Socket socket = null;

    ///
    ///param: mainActivity: the activity that is using mainActivity
    public SocketClientThread(String host, int port, ISocketClientThread mainActivity)
    {
        this.host = host;
        this.port = port;
        this.mainActivity = mainActivity;
    }

    private void openSocket() throws IOException  //TODO: Understand how allowed and what this does - throws IOException in method signature
    {
        try
        {
            // Try and connect to socket server
            socket = new Socket();
            socket.connect(new InetSocketAddress(host, port), 1000);  // 1000ms timeout
            Log.i("RobotCommand", "Connected to " + host + " port " + port);
//            this.sendCommand(new ButtonCommand(RobotCommand.Speed, ));
        }
        catch (IOException e)
        {
            Log.e("RobotCommand", "Socket open failed: " + e.getMessage());
            //Send error message to UI
            //TODO: *****Add maybe an interface or something to make sure the activity used by SocketClientThread MUST have a handler, and a CONNECTION_ERRO
//            Message msg = mainActivity.handler.obtainMessage(mainActivity.CONNECTION_ERROR, e.getMessage());
//            mainActivity.handler.sendMessage(msg);
            //Implementation of ISocketClientThread
            Message msg = mainActivity.getHandler().obtainMessage(mainActivity.CONNECTION_ERROR, e.getMessage());
            mainActivity.getHandler().sendMessage(msg);
            throw e;  //TODO: why it explicitly throws an error?
        }
    }

    @Override  //TODO: understand this whole method run()
    public void run()
    {
        try
        {
            openSocket();  //TODO: Understand how the exception is handled
        }
        catch(IOException e)
        {
            return;
        }

        try
        {
            while(running)
            {
                synchronized (lock)
                {
                    // wait to be released to perfom action
                    lock.wait();

                    //do arm command
                    robotCommand();
                }
            }
        }
        catch(InterruptedException e)
        {
            running = false;
        }
    }

    private void robotCommand()
    {
        if(!running)
            return;

        // If socket connectin has been lost then try to reconnect
        if (socket == null || !socket.isConnected())
        {
            Log.i("RobotCommand", "Socket lost, retrying to connect");
            try
            {
                openSocket();
            }
            catch (IOException e)
            {
                running = false;
                return;
            }
        }

        //Send button command to socket
        try
        {
            PrintWriter writer = new PrintWriter(socket.getOutputStream(), true);  //TODO:Understand PrintWriter
            writer.println(buttonCommand.command());  //writer.println --> the command given by the button (ex: "FF+")
            writer.flush();
        }
        catch (IOException e)
        {
            Log.e("RobotCommand", "Socket write failed: " + e.getMessage());
            // Send error message to UI
//            Message msg = MainActivity.handler.obtainMessage(MainActivity.CONNECTION_LOST, e.getMessage());
//            MainActivity.handler.sendMessage(msg);
            Message msg = mainActivity.getHandler().obtainMessage(mainActivity.CONNECTION_LOST, e.getMessage());
            mainActivity.getHandler().sendMessage(msg);
            socket = null;
        }

        // Reset button command
        buttonCommand = null;
    }

    //TODO: Understand this
    public synchronized void sendCommand(ButtonCommand buttonCommand)
    {
        synchronized (lock)
        {
            this.buttonCommand = buttonCommand;
            lock.notify();  // Release thread to send command
        }
    }

    public void stopRunning()
    {
        synchronized (lock)
        {
            running = false;
            if (socket != null)
            {
                try
                {
                    socket.close();
                }
                catch(IOException e)
                {
                    // just ignore
                }
            }
            lock.notify();
        }
    }

}