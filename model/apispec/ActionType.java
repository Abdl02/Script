package com.digitinary.dgate.model.apispec;

import com.digitinary.dgate.exception.BadRequestException;
import com.digitinary.dgate.exception.ErrorCode;
import com.fasterxml.jackson.annotation.JsonCreator;

/**
 * API Spec action type.
 *
 * @author Salah Abu Msameh
 * @since 20/11/2023
 */
public enum ActionType {

    UNLOCK_DESIGN_MODE, RESET_REVISION;

    /**
     * from value.
     *
     * @param type                 type
     * @return ApiActionType       Api Action Type
     * @throws BadRequestException BadRequestException
     */
    @JsonCreator
    public static ActionType fromValue(final String type) {

        if (type == null || type.length() == 0) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_IS_EMPTY, "actionType");
        }

        try {
            return ActionType.valueOf(type);
        } catch (IllegalArgumentException ex) {
            throw new BadRequestException(ErrorCode.FIELD_ENUM_INVALID_VALUE, "ActionType", type);
        }
    }
}
