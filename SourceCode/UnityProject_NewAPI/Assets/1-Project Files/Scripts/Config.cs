using System;
using System.Collections.Generic;

public class Config
{
    public static bool FEEDBACK_ENABLED = true;

    public static float FEEDBACK_THRESHOLD = 1.73f;

    public static ApplicationMode APPLICATION_MODE = ApplicationMode.Training;

    public static ExerciseType SELECTED_EXERCISE = ExerciseType.PLANKHOLD;

    /**
     * Relevant if recorded data is played back and recorded again.
     * If this is true, joint positions will be freshly calculated.
     * If false, the saved joint positions will be used.
     */
    public static bool OVERWRITE_JOINT_DATA = true;

    public static List<String> propertyNames = new List<string>
        {
            "quat9x", "quat6x", "gyro", "magn",
            "accelerometer", "linearAccel"
        };

    /**
     * Properties that should be streamed from the TeslaSuit to Unity
     */
    public static Dictionary<String, bool> StreamedProperties = new Dictionary<string, bool>
        {
            {"quat9x", true},
            {"quat6x", false},
            {"gyroscope", true},
            {"magnetometer", false},
            {"accelerometer", true},
            {"linearAccel", false},
        };

    /**
     * Properties that should be forwarded to Python
     */
    public static Dictionary<String, bool> FilteredProperties = new Dictionary<string, bool>
        {
            {"quat9x", false},
            {"quat6x", false},
            {"gyroscope", true},
            {"magnetometer", false},
            {"accelerometer", true},
            {"linearAccel", false},
        };

    private static Dictionary<String, uint> sensorMaskMap = new Dictionary<string, uint>
        {
            {"quat9x", 1},
            {"quat6x", 2},
            {"gyroscope", 4},
            {"magnetometer", 8},
            {"accelerometer", 16},
            {"linearAccel", 32},
        };



    public static uint TsMocapSensorMask()
    {
        uint sensorMask = 0;
        foreach (var keyValuePair in sensorMaskMap)
        {
            if (StreamedProperties[keyValuePair.Key])
            {
                sensorMask = sensorMask | keyValuePair.Value;
            }
        }

        return sensorMask;
    }
}


