package com.example.amaan.selfdrivingcarcontroller;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

public class MainMenuActivity extends AppCompatActivity {

    private Button openCtdDiscreteTurnBtn;
    private Button openCtdSteeringAngleBtn;
    private Button openAutonomousModeBtn;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_menu);
        setTitle("SDC Controller - Main Menu");
        initializeButtons();
    }

    public void initializeButtons()
    {
        openCtdDiscreteTurnBtn = (Button)findViewById(R.id.openCtdDiscreteTurnBtn);
        openCtdDiscreteTurnBtn.setOnClickListener(openCtdDiscreteTurnBtnClickHandler);

        openCtdSteeringAngleBtn = (Button)findViewById(R.id.openCtdSteeringAnglesBtn);
        openCtdSteeringAngleBtn.setOnClickListener(openCtdSteeringAngleBtnClickHandler);

        openAutonomousModeBtn = (Button)findViewById(R.id.openAutonomousModeBtn);
        openAutonomousModeBtn.setOnClickListener(openAutonomousModeClickHandler);
    }

    private View.OnClickListener openCtdDiscreteTurnBtnClickHandler = new View.OnClickListener()
    {
        @Override
        public void onClick(View v)
        {
            Intent intent = new Intent(MainMenuActivity.this, CTD_DiscreteTurnsActivity.class);
            startActivity(intent);
        }
    };

    private View.OnClickListener openCtdSteeringAngleBtnClickHandler= new View.OnClickListener()
    {
        @Override
        public void onClick(View v)
        {
            Intent intent = new Intent(MainMenuActivity.this, CTD_SteeringAngleActivity.class);
            startActivity(intent);
        }
    };

    private View.OnClickListener openAutonomousModeClickHandler = new View.OnClickListener()
    {
        @Override
        public void onClick(View v)
        {
            Intent intent = new Intent(MainMenuActivity.this, AutonomousModeActivity.class);
            startActivity(intent);
        }
    };



}
