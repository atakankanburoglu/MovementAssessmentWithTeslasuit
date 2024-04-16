using System.Collections.Generic;
using UnityEngine;
using TsAPI.Types;
using UnityEngine.UI;
using TMPro;
using Newtonsoft.Json;
using System;

public class TrainingManager : MonoBehaviour
{
    //Model Setting Panel
    [SerializeField]
    private Dropdown algorithmDropDownModel;
    [SerializeField]
    private Dropdown trainingTypeDropDownModel;
    [SerializeField]
    private TMP_InputField subjectIDsInput;
    [SerializeField]
    private Toggle validationToggle;
    [SerializeField]
    private GameObject modelSettingPanel;

    public TsHumanAnimator tsHumanAnimator;

    private DataGateway dataGateway;


    void Start()
    {
        dataGateway = FindObjectOfType<DataGateway>();

        FillTrainingTypeDropDownModel();
        FillAlgorithmDropDownModel();
    }

    void Update()
    {
        
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

    public void CreateNewModel()
    {
        if (subjectIDsInput.text == string.Empty)
        {
            Debug.LogError("Please enter subject id(s)");
            return;
        } else
        {
            Algorithm algorithm = (Algorithm)Enum.Parse(typeof(Algorithm), algorithmDropDownModel.options[algorithmDropDownModel.value].text);
            TrainingType trainingType = (TrainingType)Enum.Parse(typeof(TrainingType), trainingTypeDropDownModel.options[trainingTypeDropDownModel.value].text);
            dataGateway.PythonClient.CreateNewModel(subjectIDsInput.text, trainingType, algorithm, validationToggle.isOn);
        }
        
    }

    public void Cancel()
    {
        modelSettingPanel.SetActive(true);
    }
}
