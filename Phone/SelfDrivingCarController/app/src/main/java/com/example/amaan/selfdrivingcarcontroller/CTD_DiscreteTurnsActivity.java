package com.example.amaan.selfdrivingcarcontroller;

import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;

public class CTD_DiscreteTurnsActivity extends AppCompatActivity implements ISocketClientThread, SenderInterface {

    private SocketClientThread socketClientThread;
    public static Handler handler;
    private Sender sender;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ctd__discrete_turns);
        setTitle("CTD w/ Discrete Turns");
    }

    public SocketClientThread getSocketClientThread() {return socketClientThread;}
    public Handler getHandler(){return handler;}
    public Sender getSender() {return sender;}
}
