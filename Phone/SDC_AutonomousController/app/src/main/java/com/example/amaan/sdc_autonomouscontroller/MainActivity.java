package com.example.amaan.sdc_autonomouscontroller;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Handler;
import android.os.Message;
import android.preference.PreferenceManager;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.CompoundButton;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

public class MainActivity extends AppCompatActivity implements SenderInterface, SeekBar.OnSeekBarChangeListener{

    private SocketClientThread socketClientThread;
    private Sender sender;
    public static Handler handler;

    private SeekBar speedBar;
    private TextView speedValueTextView;
    private ToggleButton toggleAutonomousButton;

    private ButtonCommand startAutonomousButtonCmd;
    private ButtonCommand stopAutonomousButtonCmd;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        handler = new MessageHandler(this);

        sender = new Sender(this);
        setContentView(R.layout.activity_main);
        initialiseButtons();
    }

//    @Override
//    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
//    {
//        // Setup the listener
//
//        return view;
//    }

    @Override
    protected void onStart()
    {
        super.onStart();
        //Start the socket thread
        startSocketClient();

        SharedPreferences sharedPref = PreferenceManager.getDefaultSharedPreferences(this);
        final String stream = sharedPref.getString(MainActivitySettings.STREAM_KEY, "http://192.168.1.13:8090/stream");

        //Web View streaming below
//        // Set web view content to be the raspberry pi camera stream
//        final WebView webView = (WebView)findViewById(R.id.webView);
//        int default_zoom_level=175;
//        webView.setInitialScale(default_zoom_level);
//
//        // Get the width and height of the view because its different for different phone or table layouts
//        // Pass these values to the URL in teh web view to display th eHTTP stream
//        webView.post(new Runnable()
//        {
//            @Override
//            public void run() {
//                int width = webView.getWidth();
//                int height = webView.getHeight();
//                webView.loadUrl(stream + "?width="+width+"&height="+height); //TODO: Changed to 300 instead of width or height
//            }
//        });
//
//        // Clicking on webview reloads webpage
//        webView.setOnClickListener(new View.OnClickListener()
//        {
//            @Override
//            public void onClick(View v)
//            {
//                ((WebView) v).reload();
//            }
//        });

    }

    @Override
    public void onPause()
    {
        super.onPause();
        Log.i("MoveButtonsFragment", "onPause()");
        if(toggleAutonomousButton.isChecked())
        {
            toggleAutonomousButton.setChecked(false);
        }
        sender.sendButtonCommand(stopAutonomousButtonCmd);
    }

    @Override
    protected void onStop()
    {
        clearAll();

        super.onStop();
    }

    private void clearAll()
    {
        // Clear the web view
//        WebView webView = (WebView)findViewById(R.id.webView);
//        webView.loadUrl("about:blank");

        // App has been stopped so close the socket and stop thread
        socketClientThread.stopRunning();
    }

    public void initialiseButtons()
    {
        //Initialize Speed bar
        speedBar = (SeekBar) findViewById(R.id.SpeedBar);
        speedBar.setOnSeekBarChangeListener(this); //Use 'this' b/c MainActivity class implements SeekBar.OnSeekBarChangeListener Interface
        speedBar.setProgress(8);
        speedValueTextView = (TextView)findViewById(R.id.SpeedValueTextView);

        //Initialize Toggle Autonomous button
        toggleAutonomousButton = (ToggleButton) findViewById(R.id.ToggleAutonomousButton);
        toggleAutonomousButton.setOnCheckedChangeListener(ToggleAutonomousButtonHandler);
        startAutonomousButtonCmd = new ButtonCommand(RobotCommand.StartAutonomous);
        stopAutonomousButtonCmd = new ButtonCommand(RobotCommand.StopAutonomous);
    }


    private void startSocketClient()
    {
        // Load connection settings - this may have just ben changed in the preferences activity
        SharedPreferences sharedPref = PreferenceManager.getDefaultSharedPreferences(this);
        String host = sharedPref.getString(MainActivitySettings.HOST_KEY, "192.168.1.13");
        String port = sharedPref.getString(MainActivitySettings.PORT_KEY, "5000");

        // Start the socket connection thread
        socketClientThread = new SocketClientThread(host, Integer.parseInt(port));
        socketClientThread.start();
    }

    @Override
    public void onDestroy()
    {
        super.onDestroy();
        clearAll();
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu)
    {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main_activity_menu, menu);
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
//        else if (id == R.id.action_stop)
//        {
//            sendStop();
//        }

        return super.onOptionsItemSelected(item);
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
        Intent intent = new Intent(this, MainActivitySettings.class);
        startActivity(intent);
    }

    public final static int CONNECTION_ERROR = 0;
    public final static int CONNECTION_LOST = 1;

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

    public SocketClientThread getSocketClientThread()
    {
        return socketClientThread;
    }
    public Sender getSender() {return sender;}


    public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser)
    {
        Log.i("SliderEventHandler", "Progress: " + progress);
        try {
            // Only make SpeedBar increase for intervals of speedBarInterval (5)
            int speed = progress * 5;
            sender.sendButtonCommand(new ButtonCommand(RobotCommand.Speed, speed));
            speedValueTextView.setText(String.valueOf(speed));
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
    private CompoundButton.OnCheckedChangeListener ToggleAutonomousButtonHandler = new CompoundButton.OnCheckedChangeListener()
    {
        @Override
        public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
            if(isChecked) {
                Log.i("MainActivity", "ToggleAutonmousButton isChecked=TRUE");
                sender.sendButtonCommand(startAutonomousButtonCmd);  //Send Forward move command
            }
            else {
                Log.i("MainActivity", "ToggleAutonmousButton isChecked=FALSE");
                sender.sendButtonCommand(stopAutonomousButtonCmd);  // #TODO: Changed to STOP_All_motors, removed BM_motor
            }
        }
    };

}
