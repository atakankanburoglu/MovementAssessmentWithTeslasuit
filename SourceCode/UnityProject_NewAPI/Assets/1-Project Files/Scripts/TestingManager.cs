using System.Collections.Generic;
using UnityEngine;
using TsAPI.Types;
using UnityEngine.UI;
using TMPro;
using Newtonsoft.Json;
using System;
using TsSDK;

public class TestingManager : MonoBehaviour
{
    //Real Time Testing Setting Panel
    [SerializeField]
    private TMP_InputField subjectIDsInput;
    [SerializeField]
    private Dropdown algorithmDropDown;
    [SerializeField]
    private GameObject realTimeSettingPanel;
    [SerializeField]
    private TMP_InputField measurementSetsInput;

    //Recorded Testing Setting Panel
    [SerializeField]
    private TMP_InputField subjectIDsRecordedInput;
    [SerializeField]
    private TMP_InputField measurementSetsRecordedInput;
    [SerializeField]
    private Dropdown algorithmRecordedDropDown;
    [SerializeField]
    private TMP_Dropdown recordedExercisesDropDown;
    private int recordedExercisesDropDownOption;
    [SerializeField]
    private GameObject recordedSettingPanel;

    [SerializeField]
    private TMP_InputField recognizedExerciseOutput;
    [SerializeField]
    private GameObject recognizedExercisePanel;

    [SerializeField]
    private TsHapticPlayer m_hapticPlayer;

    [Range(1, 150)]
    public int frequency;

    [Range(1, 100)]
    public int amplitude;

    [Range(1, 320)]
    public int pulseWidth;

    [Range(10, 10000)]
    public int durationMs;

    public bool looped = false;

    public int currentChannelIndex = 0;

    public TsHumanBoneIndex TargetBoneIndex = TsHumanBoneIndex.LeftThumbDistal;

    private IHapticDynamicPlayable m_hapticPlayable;

    private Dictionary<TsHumanBoneIndex, List<IMapping2dElectricChannel>> m_channels = new Dictionary<TsHumanBoneIndex, List<IMapping2dElectricChannel>>();


    //Feedback Panel
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
    private float timeInterval = 10.0f;

    public TsHumanAnimator tsHumanAnimator;

    private ExerciseType exerciseType;

    List<string> recordedExercisesList = new List<string>();

    [SerializeField]
    private Text startCountdown;
    [SerializeField]
    private Text timerCountdown;

    void Start()
    {
        FillAlgorithmDropDownModel();
    }

    void Update()
    {
        if (startCountdown.text == "0") {
            timeInterval -= Time.deltaTime;
            if (running)
            {
                timerCountdown.gameObject.SetActive(true);
                timerCountdown.text = (timeInterval).ToString("0");

                ImuDataObject imuDataObject = new ImuDataObject(exerciseType, tsHumanAnimator.ImuData, timeInterval);
                dataGateway.PushSuitData(ApplicationMode.Testing, imuDataObject);
            }
        }
        if (recordedExercisesList.Count != 0)
        {
            FillRecordedExercisesDropDownModel();
        }
        else
        {
            dataGateway.GetRecordedExercises();
        }
        if (timeInterval < 0)
        {
            timeInterval = 10.0f;
        }
        recordedExercisesDropDown.value = recordedExercisesDropDownOption;
    }

    public void FillRecognizedExcerciseOutputInput(ExerciseType exerciseType)
    {
        this.exerciseType = exerciseType;
        recognizedExerciseOutput.text = Enum.GetName(typeof(ExerciseType), exerciseType);
    }


    void FillAlgorithmDropDownModel()
    {
        List<String> algorithms = new List<String>(Enum.GetNames(typeof(Algorithm)));
        int index = algorithms.IndexOf("SVM");
        algorithms.RemoveAt(index);
        algorithmDropDown.ClearOptions();
        algorithmDropDown.AddOptions(new List<string>(algorithms));
        algorithmRecordedDropDown.ClearOptions();
        algorithmRecordedDropDown.AddOptions(new List<string>(algorithms));
    }

    public void StartRealTimeTestingMode()
    {
        Algorithm algorithm = (Algorithm)Enum.Parse(typeof(Algorithm), algorithmDropDown.options[algorithmDropDown.value].text);
        ModelDataObject modelDataObject = new ModelDataObject(subjectIDsInput.text, ExerciseType.PLANKHOLD, algorithm, measurementSetsInput.text);
        dataGateway.StartRealTimeTestingMode(modelDataObject);
    }
    void FillRecordedExercisesDropDownModel()
    {
        recordedExercisesDropDown.ClearOptions();
        List<TMP_Dropdown.OptionData> optionList = new List<TMP_Dropdown.OptionData>();
        foreach (String recordedExercises in recordedExercisesList)
        {
            var newOption = new TMP_Dropdown.OptionData();
            newOption.text = recordedExercises;
            optionList.Add(newOption);
        }
        recordedExercisesDropDown.AddOptions(optionList);
    }

    public void SetRecordedExercisesForDropdown(string[] recordedExercises)
    {
        this.recordedExercisesList = new List<string>(recordedExercises);
    }

    public void SaveRecordedExerciseDropdownOption()
    {
        recordedExercisesDropDownOption = recordedExercisesDropDown.value;
    }
    public void StartRecordedTestingMode()
    {
        Algorithm algorithm = (Algorithm)Enum.Parse(typeof(Algorithm), algorithmRecordedDropDown.options[algorithmRecordedDropDown.value].text);
        ModelDataObject modelDataObject = new ModelDataObject(subjectIDsRecordedInput.text, ExerciseType.PLANKHOLD, algorithm, measurementSetsRecordedInput.text);
        String recordedExercise = recordedExercisesDropDown.options[recordedExercisesDropDown.value].text;
        dataGateway.StartRecordedTestingMode(modelDataObject, recordedExercise);
    }

    public void GiveFeedback(Dictionary<TsHumanBoneIndex, int> feedback)
    {
        foreach (var boneIndex in TsHumanBones.SuitBones)
        {
            if(feedback.TryGetValue(boneIndex, out int value))
            {
                frequency = 150 * value;
                amplitude = 100 * value;
                pulseWidth = 320 * value;
                TargetBoneIndex = boneIndex;
                //Play(currentChannelIndex); 
                //TODO: show feedback through arrow
            }
        }
    }

    private void Validate()
    {
        ValidateChannels();
        if (m_hapticPlayable != null)
        {
            m_hapticPlayable.Stop();
        }

        m_hapticPlayable = m_hapticPlayer.CreateTouch(frequency, amplitude, pulseWidth, durationMs);
        m_hapticPlayable.IsLooped = looped;
    }

    private void ValidateChannels()
    {
        m_channels.Clear();
        var channels = m_hapticPlayer.Device.Mapping2d.ElectricChannels;
        foreach (var channel in channels)
        {
            if (!m_channels.ContainsKey(channel.BoneIndex))
            {
                m_channels.Add(channel.BoneIndex, new List<IMapping2dElectricChannel>());
            }
            m_channels[channel.BoneIndex].Add(channel);
        }
    }

    public void Play(int channelIndex)
    {
        Validate();

        if (!m_channels.TryGetValue(TargetBoneIndex, out var channelsGroup))
        {
            return;
        }

        var index = channelIndex % channelsGroup.Count;
        var channel = channelsGroup[index];
        m_hapticPlayable.Play();
        m_hapticPlayable.AddChannel(channel);
    }


    public void StartFeedback()
    {
        running = true;
        timeInterval = 10.0f;
    }
    public void PauseFeedback()
    {
        running = false;
        m_hapticPlayable.IsPaused = !m_hapticPlayable.IsPaused;
    }
    public void StopFeedback()
    {
        running = false;

        timerCountdown.gameObject.SetActive(false);
        timeInterval = 10.0f;

        m_hapticPlayable.Stop();
    }

    public void Cancel()
    {
        FillAlgorithmDropDownModel();
        feedbackPanel.SetActive(false);
        realTimeSettingPanel.SetActive(true);
        recordedSettingPanel.SetActive(true);
        recognizedExercisePanel.SetActive(false);
        timerCountdown.gameObject.SetActive(false);
        timeInterval = 10.0f;
        running = false;
    }
}
