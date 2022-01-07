package com.example.amaan.selfdrivingcarcontroller;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.EditTextPreference;
import android.preference.Preference;
import android.preference.PreferenceActivity;

import java.util.ArrayList;

/**
 * Created by amaan on 11/23/2017.
 */

//TODO: when adding more settings from different activities, create fragments. Example in link below in TODO comment
public class SettingsActivity extends PreferenceActivity implements SharedPreferences.OnSharedPreferenceChangeListener
{
    public static final String HOST_KEY = "host";
    public static final String PORT_KEY = "port";
//    public static final String STREAM_KEY = "stream";
//    private String[] mPreferenceKeys = {HOST_KEY, PORT_KEY, STREAM_KEY};
    private String[] mPreferenceKeys = {HOST_KEY, PORT_KEY};

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        addPreferencesFromResource(R.xml.activity_settings); //TODO: Alternative to the deprecated version: https://stackoverflow.com/a/13441715/7359915
        SharedPreferences prefs = getPreferenceManager().getSharedPreferences();

        // Load the existing preferences into teh summary screen
        ArrayList<Preference> mPreferences = new ArrayList<Preference>();
        for (String prefKey : mPreferenceKeys) {
            Preference pref = (Preference) getPreferenceManager().findPreference(prefKey);
            mPreferences.add(pref);
            onSharedPreferenceChanged(prefs, prefKey);
        }
    }

    @Override
    public void onSharedPreferenceChanged(SharedPreferences sharedPreferences, String key)
    {
        Preference pref = findPreference(key);

        // Reset the summary text with the new value
        if (pref instanceof EditTextPreference) {
            EditTextPreference prefText = (EditTextPreference) pref;
            prefText.setSummary(prefText.getText());
        }
    }
}
