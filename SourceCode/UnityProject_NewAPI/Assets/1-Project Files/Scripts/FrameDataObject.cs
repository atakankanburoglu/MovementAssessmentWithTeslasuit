using System;
using System.Collections.Generic;
using System.Text;


[Serializable]
public class FrameDataObject
{
    public ApplicationMode applicationMode;
    public State state;
    public String payload;

    public FrameDataObject(ApplicationMode applicationMode, State state, String payload)
    {
        this.applicationMode = applicationMode;
        this.state = state;
        this.payload = payload;
    }

    override
    public String ToString()
    {
        StringBuilder sb = new StringBuilder();
        sb.Append(applicationMode).Append(" ");
        sb.Append(state).Append(";");
        sb.Append(payload);
        return sb.ToString();
    }

}
