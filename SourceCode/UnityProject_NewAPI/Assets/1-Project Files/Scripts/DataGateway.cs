using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using System;

public class DataGateway : MonoBehaviour
{

    private PythonClient pythonClient;

    [SerializeField]
    private TestingManager testingManager;
    void Start()
    {
        pythonClient = new PythonClient();
    }

    // Update is called once per frame
    void Update()
    {

    }

    public void PushSuitData(ApplicationMode applicationMode, ImuDataObject imuDataObject)
    {
        FrameDataObject frameDataObject = new FrameDataObject(applicationMode, State.RUNNING, imuDataObject.ToCSV(","));
        pythonClient.PushData(frameDataObject);
    }

    
    public void StartRecording()
    {
        //dummy
        ImuDataObject imuDataObject = new ImuDataObject();
        FrameDataObject frameDataObject = new FrameDataObject(ApplicationMode.Recording, State.INIT, imuDataObject.GetCsvHeader(","));
        pythonClient.PushData(frameDataObject);
    }

    public void SaveRecording(SampleDataObject sampleData)
    {
        FrameDataObject frameDataObject = new FrameDataObject(ApplicationMode.Recording, State.FINISHED, sampleData.ToString());
        pythonClient.PushData(frameDataObject);
    }

    public void TrainModel(ModelDataObject modelData, Boolean validate)
    {

        FrameDataObject frameDataObject = new FrameDataObject(ApplicationMode.Training, State.RUNNING, modelData.ToString() + ";" + validate);
        pythonClient.PushData(frameDataObject);
    }

    public void StartRealTimeTestingMode(ModelDataObject modelData)
    {
        //dummy
        ImuDataObject imuDataObject = new ImuDataObject();
        FrameDataObject frameDataObject = new FrameDataObject(ApplicationMode.Testing, State.INIT, modelData.ToString() + ";" + imuDataObject.GetCsvHeader(","));
        pythonClient.PushData(frameDataObject);
    }

    public void StartRecordedTestingMode(ModelDataObject modelData, String recordedExercise)
    {
        FrameDataObject frameDataObject = new FrameDataObject(ApplicationMode.Testing, State.RECORDED, modelData.ToString() + ";" + recordedExercise);
        pythonClient.PushData(frameDataObject);
    }

        public void GetRecordedExercises()
    {
        FrameDataObject frameDataObject = new FrameDataObject(ApplicationMode.Testing, State.IDLE, "");
        pythonClient.PushData(frameDataObject);
    }

    public void OnExcerciseRecognized(string exercise)
    {
        ExerciseType exerciseType = (ExerciseType)Enum.Parse(typeof(ExerciseType), exercise);
        testingManager.FillRecognizedExcerciseOutputInput(exerciseType);
    }

    public void OnRecordedExercisesListReceived(string recordedExercisesList)
    {
        var recordedExercises = recordedExercisesList.Split(',');
        testingManager.SetRecordedExercisesForDropdown(recordedExercises);
    }

    private void OnDestroy()
    {
        pythonClient.Stop();
    }
}
