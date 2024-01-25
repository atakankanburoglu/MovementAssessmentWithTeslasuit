using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ReplayObject
{
    public string subjectName;
    public List<ReplayInfo> replayInfo = new List<ReplayInfo>();
    public TrainingType trainingType = TrainingType.Plank_Hold;

    public ReplayObject() { }
    public ReplayObject(string name, List<ReplayInfo> info, TrainingType training)
    {
        subjectName = name;
        replayInfo = info;
        trainingType = training;
    }
    // public List<float> timeStamp;   
}