package com.example.amaan.selfdrivingcarcontroller;

import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Message;
import android.preference.PreferenceManager;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

import java.net.Socket;

import io.github.controlwear.virtual.joystick.android.JoystickView;

public class CTD_SteeringAngleActivity extends AppCompatActivity implements SeekBar.OnSeekBarChangeListener, ISocketClientThread, SenderInterface {

    public static Handler handler;
    private Sender sender;
    private SocketClientThread socketClientThread;

    private TextView speedTextView;
    private TextView steerAngleTextView;
    private SeekBar speedBar;
    private ToggleButton toggleFwdBtn;
    private ToggleButton toggleTrainingSessionBtn;
    private Button stopAllBtn;

    private int currentSteerAngle;
    private String steerAngleText;
    private String speedText;

    private ButtonCommand fwdBtnCmd;
    private ButtonCommand stopAllCmd;
    private ButtonCommand startTrainingSessionCmd;
    private ButtonCommand pauseTrainingSessionCmd;

    AlertDialog.Builder saveDiscardDataDialog;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ctd__steering_angle);
        setTitle("CTD w/ Steering Angles");
        this.currentSteerAngle = 0;
        speedText ="Speed: %d";
        steerAngleText = "Steer Angle: %d";

        handler = new MessageHandler(this);
        sender = new Sender(this);

        //Initialise Dialog box
        initSaveDiscardDataDialog();

        JoystickView joystick = (JoystickView) findViewById(R.id.joystickView);
        joystick.setOnMoveListener(new JoystickView.OnMoveListener() {
            @Override
            public void onMove(int angle, int strength) {
                int newSteerAngle = getSteerAngle(angle, strength);
                try {
                    if (newSteerAngle != currentSteerAngle)//send steerAngle if its different. dont send if its same
                    {
                        currentSteerAngle = newSteerAngle;
                        sender.sendButtonCommand(new ButtonCommand(RobotCommand.SteerAngle, currentSteerAngle));
                        steerAngleTextView.setText(String.valueOf(currentSteerAngle));
                        Log.i("onMove Joystick", "SteerAngle: "+ currentSteerAngle);
                    }
                }
                catch(NullPointerException e){
                 Log.w("SocketClientThread:", "Cannot send steer angle, Message: " + e.getMessage());
                }
            }
        });
    }

    private void initSaveDiscardDataDialog()
    {
        saveDiscardDataDialog = new AlertDialog.Builder(this);
        saveDiscardDataDialog.setMessage("Would you like to DISCARD or SAVE data from last auto save?");
        saveDiscardDataDialog.setTitle("Save or Discard Training Data");
//            saveDiscardDataDialog.setCancelable(true);

        saveDiscardDataDialog.setPositiveButton(
                "SAVE",
                new DialogInterface.OnClickListener(){
                    public void onClick(DialogInterface dialog, int id){
                        sender.sendButtonCommand(new ButtonCommand(RobotCommand.SaveTS));
                        Log.i("saveDiscardDataDialog", "SAVE Clicked");
                    }
                }
        );
        saveDiscardDataDialog.setNegativeButton(
                "Discard",
                new DialogInterface.OnClickListener(){
                    public void onClick(DialogInterface dialog, int id){
                        sender.sendButtonCommand(new ButtonCommand(RobotCommand.DiscardTS));
                        Log.i("saveDiscardDataDialog", "DISCARD Clicked");
                    }
                }
        );
    }

    private void initializeViews()
    {
        speedBar = (SeekBar)findViewById(R.id.speedBar);
        speedBar.setOnSeekBarChangeListener(this); //Make sure to implement SeekBar.OnSeekBarChangeListener Interface
        speedBar.setProgress(8);

        speedTextView = (TextView) findViewById(R.id.speedTextView);

        steerAngleTextView = (TextView)findViewById(R.id.steerAngleTextView);

        toggleFwdBtn = (ToggleButton)findViewById(R.id.toggleMoveForwardButton);
        toggleFwdBtn.setOnCheckedChangeListener(FwdBtnToggleHandler);
        fwdBtnCmd = new ButtonCommand(RobotCommand.Forward);
        //NOTE: Removed Command State (fwdButtonCmd.setCommandState(CommandState.Moving)

        stopAllBtn = (Button)findViewById(R.id.StopAllBtn);
        stopAllBtn.setOnClickListener(stopAllBtnClickHandler);
        stopAllCmd = new ButtonCommand(RobotCommand.AllMotorStop);

        toggleTrainingSessionBtn = (ToggleButton)findViewById(R.id.toggleTrainingSessionBtn);
        toggleTrainingSessionBtn.setOnCheckedChangeListener(ToggleTrainingSessionHandler);
        startTrainingSessionCmd = new ButtonCommand(RobotCommand.StartTrainingSession);
        pauseTrainingSessionCmd = new ButtonCommand(RobotCommand.PauseTrainingSession);
    }


    private CompoundButton.OnCheckedChangeListener ToggleTrainingSessionHandler = new CompoundButton.OnCheckedChangeListener() {
        @Override
        public void onCheckedChanged(CompoundButton compoundButton, boolean isChecked) {
            if(isChecked){
                // Send Start Training Session Cmd
                sender.sendButtonCommand(startTrainingSessionCmd);
                Log.i("MoveButtonsFragment", "START TRAINING CMD SENT");
            }
            else{
                sender.sendButtonCommand(pauseTrainingSessionCmd);
                Log.i("MoveButtonsFragment", "PAUSE TRAINING SESSION Cmd Sent");
                AlertDialog alertDialog = saveDiscardDataDialog.create();
                alertDialog.show();
            }
        }
    };


    private View.OnClickListener stopAllBtnClickHandler = new View.OnClickListener()
    {
        @Override
        public void onClick(View v)
        {
            Log.i("MoveButtonsFragment", "All Motor Stop Button Click Handler");
            sender.sendButtonCommand(stopAllCmd);
//            toggleBackBtn.setChecked(false);
            toggleFwdBtn.setChecked(false);
        }
    };



    private CompoundButton.OnCheckedChangeListener FwdBtnToggleHandler = new CompoundButton.OnCheckedChangeListener()
    {
        @Override
        public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
            if(isChecked) {
                Log.i("MoveButtonsFragment", "FwdToggleBtn isChecked=TRUE");
                // If BackBtnToggleHandler isChecked - Then uncheck it - and send Fwd Cmd, the Python rpi program will off back motor
//                if(toggleBackBtn.isChecked() == true)
//                    toggleBackBtn.toggle();  //If ToggleFackBtn is checked when FwdBtn is checked, then uncheck BackBtn
                sender.sendButtonCommand(fwdBtnCmd);  //Send Forward move command
            }
            else {
                Log.i("MoveButtonsFragment", "FwdToggleBtn isChecked=FALSE");
                sender.sendButtonCommand(stopAllCmd);  // #TODO: Changed to STOP_All_motors, removed BM_motor
            }
        }
    };

    private int getSteerAngle(int joyStickAngle, int joyStickStrength)
    {
        int steerAngle = (int)(((double)joyStickStrength/10));
        if(joyStickAngle == 180) //it equals 180 when joystick on left side
            steerAngle *= -1; //turn to negative cause left
        return steerAngle;
    }

    @Override
    protected void onStart()
    {
        super.onStart();
        //Start the socket thread
        startSocketClient();
        initializeViews();
    }

    public boolean onCreateOptionsMenu(Menu menu)
    {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.activity_quickbar, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item)
    {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings)
        {
            launchSettingsActivity();
            return true;
        }
        else if (id == R.id.action_reconnect)
        {
            reconnect();
        }

        return super.onOptionsItemSelected(item);
    }

    protected void onStop()
    {
        clearAll();
        super.onStop();
    }

    private void clearAll()
    {
        socketClientThread.stopRunning();
    }
    private void startSocketClient(){
        // Load connection settings - this may have just ben changed in the preferences activity
        SharedPreferences sharedPref = PreferenceManager.getDefaultSharedPreferences(this);
        String host = sharedPref.getString(SettingsActivity.HOST_KEY, "192.168.1.13");
        String port = sharedPref.getString(SettingsActivity.PORT_KEY, "5000");

        // Start the socket connection thread
        socketClientThread = new SocketClientThread(host, Integer.parseInt(port), this);
        socketClientThread.start();
    }

    @Override
    public void onDestroy()
    {
        super.onDestroy();
        clearAll();
    }

    /**
     * Menu method to reconnect
     */
    private void reconnect()
    {
        socketClientThread.stopRunning();
        startSocketClient();
    }


    /**
     * Launch the settings menu
     */
    private void launchSettingsActivity()
    {
        Intent intent = new Intent(this, SettingsActivity.class);
        startActivity(intent);
    }


    public SocketClientThread getSocketClientThread() {return socketClientThread;}
    public Handler getHandler(){return handler;}
    public Sender getSender() {return sender;}

    /**
     * Message handler class used to process error messages from socket thread
     */
    private static class MessageHandler extends Handler
    {
        private Context context;
        private MessageHandler(Context context)
        {
            this.context = context;
        }

        @Override
        public void handleMessage(Message msg)
        {
            switch (msg.what)
            {
                case CONNECTION_ERROR:
                    message("Can't connect to the arm");
                    break;
                case CONNECTION_LOST:
                    message("Connection lost to the arm");
                    break;
            }
        }
        void message(String message)
        {
            Toast.makeText(context, message, Toast.LENGTH_LONG).show();
        } //todo:understand this
    }

    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser)
    {
        //Send the new speed to the robot
//        buttonDispatcher.buttonCommand(new ButtonCommand(RobotCommand.Speed, progress));
        Log.i("Speed bar:", "Progress" + progress);
        try {
            // Only make SpeedBar increase for intervals of speedBarInterval (5)
            int speed = progress * 5;
            sender.sendButtonCommand(new ButtonCommand(RobotCommand.Speed, speed));
            speedTextView.setText(String.valueOf(speed));
        }
        catch(NullPointerException e){
            Log.w("SocketClientThread:", "Cannot send speed - Null Reference SocketClientThread Obj");
        }
    }

    @Override
    public void onStartTrackingTouch(SeekBar seekBar)
    {
    }

    @Override
    public void onStopTrackingTouch(SeekBar seekBar)
    {
    }
}
