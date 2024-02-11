using System.Collections.Generic;
using UnityEngine;
using TsAPI.Types;
using UnityEngine.UI;
using TMPro;
using Newtonsoft.Json;
using System;

public class TestingManager : MonoBehaviour
{
    //Model Setting Panel
    [SerializeField]
    private Dropdown algorithmDropDownModel;
    [SerializeField]
    private Dropdown crossValidationDropDown;
    [SerializeField]
    private GameObject modelSettingPanel;

    [SerializeField]
    private TMP_InputField recognizedExerciseOutput;

    //Recording Panel
    [SerializeField]
    private GameObject startButton;
    [SerializeField]
    private GameObject pauseButton;
    [SerializeField]
    private GameObject stopButton;
    [SerializeField]
    private GameObject feedbackPanel;

    public DataGateway dataGateway;

    private Boolean running;

    public TsHumanAnimator tsHumanAnimator;

    private TrainingType trainingType;
    void Start()
    {
        FillTrainingTypeDropDownModel();
        FillAlgorithmDropDownModel();
    }

    void Update()
    {
        if (running)
        {
            ImuDataObject imuDataObject = new ImuDataObject(trainingType, tsHumanAnimator.ImuData, Time.time);
            dataGateway.PythonClient.PushSuitData(imuDataObject);
        }
    }

    public void FillRecognizedExcerciseOutputInput(TrainingType trainingType)
    {
        recognizedExerciseOutput.text = Enum.GetName(typeof(TrainingType), trainingType);
    }
    void FillTrainingTypeDropDownModel()
    {
        string[] names = Enum.GetNames(typeof(TrainingType));
        trainingTypeDropDownModel.ClearOptions();
        trainingTypeDropDownModel.AddOptions(new List<string>(names));
    }

    void FillAlgorithmDropDownModel()
    {
        string[] names = Enum.GetNames(typeof(Algorithm));
        algorithmDropDownModel.ClearOptions();
        algorithmDropDownModel.AddOptions(new List<string>(names));
    }

    public void ChooseModel()
    {
        Algorithm algorithm = (Algorithm)Enum.Parse(typeof(Algorithm), algorithmDropDownModel.options[algorithmDropDownModel.value].text);
        dataGateway.PythonClient.StartTestingMode(algorithm, true);
    }

    public void StartFeedback()
    {
        running = true;
    }
    public void PauseFeedback()
    {
        running = false;
    }
    public void StopFeedback()
    {
        dataGateway.PythonClient.StopTestingMode();
        running = false;
    }
}
